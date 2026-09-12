import os,requests
class GovernmentAdapter:
    def __init__(self,base_url="",token=""): self.base_url,self.token=base_url,token
    def health(self): return {"configured":bool(self.base_url and self.token)}
    def fetch(self,path,params=None):
        if not self.base_url: return {"status":"not_configured"}
        r=requests.get(self.base_url.rstrip("/")+"/"+path.lstrip("/"),headers={"Authorization":f"Bearer {self.token}"},params=params,timeout=10); r.raise_for_status(); return r.json()
def status(name): return GovernmentAdapter(os.getenv(name+"_URL",""),os.getenv(name+"_TOKEN","")).health()
def notification_status(): return {"sms":bool(os.getenv("SMS_PROVIDER_URL")),"ivr":bool(os.getenv("IVR_PROVIDER_URL")),"push":bool(os.getenv("PUSH_PROVIDER_URL"))}
