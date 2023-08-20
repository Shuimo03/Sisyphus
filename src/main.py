import json
from abc import ABC, abstractmethod
from fastapi import FastAPI
import uvicorn
import requests
import yaml
from pydantic import BaseModel
from typing import List



class VMAction(BaseModel):
    action: str
    vm_ids: List[str]

app = FastAPI()


class VirtualMachineInterface(ABC):
    # 设计为工厂模式
    @abstractmethod
    def start(self, ids: list[str]):
        pass
    # @abstractmethod
    # def stop(self, vm_id):
    #     pass
    #

    # @abstractmethod
    # def vm_status(self, id: str):
    #     pass

    @abstractmethod
    def virtual_machine_list(self):
        pass

# 批量启动/关闭/休眠机器
# 查看每台机器状态

class VirtualMachine(VirtualMachineInterface):

    def __init__(self):
        self.config = self.load_config("../config.yaml")

    def load_config(self,filePath):
        with open(filePath, "r") as config_file:
            config = yaml.safe_load(config_file)
        return config
    def virtual_machine_list(self):
        api_url = self.config["api_url"]
        authorization = self.config["authorization"]
        headers = {
            'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
            'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
            'Authorization': authorization
        }
        resource = requests.get(api_url, headers=headers)
        return resource.json()

    # def vm_status(self, id):
    #     vm_list = self.virtual_machine_list()
    #     data_dict = json.dumps(vm_list)
    #     print(data_dict)


    # 最好提供三种模式: 单选,批次,全选
    def start(self, ids: List[str]):
        api_url = self.config["api_url"]
        authorization = self.config["authorization"]
        payload = "on"
        headers = {
            'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
            'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
            'Authorization': authorization
        }

        # http://127.0.0.1:8697/api/vms/3L85GB5H6FMU21IHMC7SRAJ8MD409J2Q/power
        for vm_id in ids:
            url = f"{api_url}/vms/{vm_id}/power"
            print("URL:" ,url)
            response = requests.put(url, headers=headers,data=payload)

            if response.status_code == 200:
                print(f"Started VM with ID: {vm_id}")
            else:
                print("Error:", response.json())


vm = VirtualMachine()

@app.get("/v1/list/vm/")
def get_vm_list():
    vm_list = vm.virtual_machine_list()
    return {"vm_list": vm_list}

# @app.get("/v1/vm/status/")
# async def vm_status(id: str):
#     vs  = vm.vm_status(id)
#     return {"vs": vs}

# JSON格式
@app.put("/v1/start/vm/")
async def start_vm(vm_action: VMAction):
    #修改为工程模式
    if vm_action.action == "start":
        vm.start(vm_action.vm_ids)
        return {"message": "Starting VMs"}
    else:
        return {"error": "Invalid action"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
