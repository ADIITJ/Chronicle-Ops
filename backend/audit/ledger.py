from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class AuditLedger:
    """Append-only audit ledger with cryptographic signatures"""
    
    def __init__(self):
        # Generate signing key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        self.entries: list[Dict[str, Any]] = []
        self.last_signature: Optional[bytes] = None
    
    def append(
        self,
        run_id: str,
        sim_time: datetime,
        entry_type: str,
        data: Dict[str, Any],
        agent_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Append entry to ledger (idempotent if entry has unique ID)"""
        
        # Check for duplicate entry ID
        entry_id = data.get('id')
        if entry_id:
            for existing in self.entries:
                if existing.get('data', {}).get('id') == entry_id:
                    return existing  # Idempotent: already recorded
        
        sequence = len(self.entries)
        timestamp = datetime.utcnow()
        
        entry = {
            'run_id': run_id,
            'sequence': sequence,
            'timestamp': timestamp.isoformat(),
            'sim_time': sim_time.isoformat(),
            'entry_type': entry_type,
            'agent_role': agent_role,
            'data': data,
            'prev_signature': self.last_signature.hex() if self.last_signature else None
        }
        
        # Sign entry
        entry_json = json.dumps(entry, sort_keys=True)
        signature = self.private_key.sign(
            entry_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        entry['signature'] = signature.hex()
        self.last_signature = signature
        
        self.entries.append(entry)
        return entry
    
    def verify_chain(self) -> bool:
        """Verify integrity of entire chain"""
        prev_sig = None
        
        for entry in self.entries:
            # Check prev_signature matches
            expected_prev = prev_sig.hex() if prev_sig else None
            if entry.get('prev_signature') != expected_prev:
                return False
            
            # Verify signature
            entry_copy = entry.copy()
            signature_hex = entry_copy.pop('signature')
            signature = bytes.fromhex(signature_hex)
            
            entry_json = json.dumps(entry_copy, sort_keys=True)
            
            try:
                self.public_key.verify(
                    signature,
                    entry_json.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            except Exception:
                return False
            
            prev_sig = signature
        
        return True
    
    def get_entries(self, run_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get entries, optionally filtered by run_id"""
        if run_id:
            return [e for e in self.entries if e['run_id'] == run_id]
        return self.entries.copy()
    
    def export_bundle(self, run_id: str) -> Dict[str, Any]:
        """Export signed audit bundle for a run"""
        entries = self.get_entries(run_id)
        
        # Create bundle
        bundle = {
            'run_id': run_id,
            'entries': entries,
            'entry_count': len(entries),
            'public_key': self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            'exported_at': datetime.utcnow().isoformat()
        }
        
        # Sign bundle
        bundle_json = json.dumps(bundle, sort_keys=True)
        bundle_signature = self.private_key.sign(
            bundle_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        bundle['bundle_signature'] = bundle_signature.hex()
        
        return bundle
    
    def get_public_key_pem(self) -> str:
        """Get public key for external verification"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
