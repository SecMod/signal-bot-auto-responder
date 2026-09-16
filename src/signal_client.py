from __future__ import annotations
import subprocess
from dataclasses import dataclass

@dataclass
class SignalClient:
    account: str
    signal_cli: str = "signal-cli"
    def _run(self,*args):
        r=subprocess.run([self.signal_cli,"-a",self.account,*args],capture_output=True,text=True,check=False)
        if r.returncode: raise RuntimeError(r.stderr.strip() or "signal-cli failed")
        return r.stdout
    def list_groups(self):
        return self._run("listGroups","--detailed")
    def send_to_group(self,group_id,message):
        if not group_id.strip() or not message.strip(): raise ValueError("group_id and message are required")
        return self._run("send","-g",group_id,"-m",message)
