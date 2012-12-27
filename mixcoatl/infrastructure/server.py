from mixcoatl.resource import Resource
from mixcoatl.admin import job
from mixcoatl.utils import wait_for_job
from mixcoatl.utils import uncamel_keys

import time
import os
import json
from collections import defaultdict

class Server(Resource):
    def __init__(self, server_id = None):
        obj_path = 'infrastructure/Server'
        self.collection_name = 'servers'
        Resource.__init__(self, obj_path)
        #if server_id is None:
        self.__server_id = None
        self.__cloud = None
        self.__datacenter = None
        self.__region = None
        self.__status = None
        self.__name = None
        self.__platform = None
        self.__budget = None
        self.__start_date = None
        self.__label = None
        self.__customer = None
        self.__description = None
        self.__firewalls = None
        self.__private_ip_addresses = None
        self.__public_ip_address = None
        self.__owning_groups = None
        self.__owning_user = None
        self.__product_id = None
        self.__provider_product_id = None
        self.__keypair = None
        self.__agent_version = None
        self.__machine_image = None
        self.__provider_id = None
        if server_id is not None:
            self.get_server(server_id)

    @property
    def server_id(self):
        '''The immutable enStratus ID of this server'''
        return self.__server_id

    @server_id.setter
    def server_id(self, sid):
        self.__server_id = sid

    @property
    def cloud(self):
        '''The id of the cloud where the instance is located'''
        return self.__cloud

    @cloud.setter
    def cloud(self, c):
        self.__cloud = c
        
    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def customer(self):
        return self.__customer

    @customer.setter
    def customer(self, c):
        self.__customer = c

    @property
    def datacenter(self):
        '''The id of the specific datacenter where the instance is located.'''
        return self.__datacenter

    @datacenter.setter
    def datacenter(self, dc):
        self.__datacenter = dc

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, desc):
        self.__description = desc

    @property
    def machine_image(self):
        return self.__machine_image

    @machine_image.setter
    def machine_image(self, mi):
        self.__machine_image = mi

    @property
    def firewalls(self):
        return self.__firewalls

    @firewalls.setter
    def firewalls(self, fw):
        self.__firewalls = fw

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, n):
        self.__name = n

    @property
    def owning_groups(self):
        return self.__owning_groups

    @owning_groups.setter
    def owning_groups(self, og):
        self.__owning_groups = og

    @property
    def owning_user(self):
        return self.__owning_user

    @owning_user.setter
    def owning_user(self, ou):
        self.__owning_user = ou

    @property
    def platform(self):
        return self.__platform

    @property
    def private_ip_addresses(self):
        return self.__private_ip_addresses

    @private_ip_addresses.setter
    def private_ip_addresses(self, ip_list):
        self.__private_ip_addresses = ip_list

    @property
    def public_ip_address(self):
        return self.__public_ip_address

    @public_ip_address.setter
    def public_ip_address(self, ip):
        self.__public_ip_address = ip

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, r):
        self.__region = r

    @property
    def platform(self):
        return self.__platform

    @platform.setter
    def platform(self, p):
        self.__platform = p

    @property
    def product_id(self):
        return self.__product_id

    @product_id.setter
    def product_id(self, pid):
        self.__product_id = pid

    @property
    def provider_product_id(self):
        return self.__provider_product_id

    @provider_product_id.setter
    def provider_product_id(self, ppid):
        self.__provider_product_id = ppid

    @property
    def provider_id(self):
        return self.__provider_id

    @provider_id.setter
    def provider_id(self, pid):
        self.__provider_id = pid

    @property
    def start_date(self):
        return self.__start_date

    @start_date.setter
    def start_date(self, date):
        self.__start_date = date

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, s):
        self.__status = s

    @property
    def budget(self):
        return self.__budget

    @budget.setter
    def budget(self, bid):
        self.__budget = bid

    def get_server(self, server_id):
        p = self.path+"/"+str(server_id)
        s = self.get(path=p)
        if self.last_error is None:
            try:
                scope = uncamel_keys(s[self.collection_name][0])
                for k in scope.keys():
                    setattr(self,k,scope[k])
#                self.server_id = server_id
#                self.budget = scope['budget']
#                self.machine_image = scope['machineImage']['machineImageId']
#                self.description = scope['description']
#                self.name = scope['name']
#                self.start_date = scope['startDate']
#                self.status = scope['status']
#                self.private_ip_addresses = scope['privateIpAddresses']
#                self.public_ip_address =  scope['publicIpAddress']
#                self.label = scope['label']
#                self.product_id = scope['product']['productId']
#                self.provider_id = scope['providerId']
#                self.provider_product_id = scope['providerProductId']
#                self.owning_user = scope['owningUser']['userId']
            except KeyError, ke:
                print("missing key "+str(ke.args))
                pass
            except AttributeError:
                print("missing attribute: "+k)
            return self
        else:
            return self.last_error

    def del_server(self, server_id, reason):
        p = self.path+"/"+str(server_id)
        params = {'reason':reason}
        return self.delete(path=p, params=params)

def list_all():
    s = Server()
    servers = s.get()
    if s.last_error is None:
        return servers['servers']
    else:
        return s.last_error

def get(server_id):
    s = Server(server_id)
    if s.last_error is None:
        return s['servers'][0]
    else:
        return s.last_error

def terminate(server_id, reason='mixcoatl terminate server'):
    s = Server()
    s.del_server(server_id, reason)
    if s.last_error is None:
        return True
    else:
        return s.last_error

# This should be abstracted a bit more....
def launch(img_id, product, dc_id, fw_id, kp=None, wait=False):
    s = Server()
    now = int(round(time.time() * 1000))
    whoami = os.environ['USER']

    payload = {'launch':
            [{
                'product':product,
                'firewalls':[{'firewallId':fw_id}],
                'machineImage':{'machineImageId':img_id},
                'description':'mixcoatl server launch',
                'name':'mixcoatl-'+whoami+'-'+str(now),
                'dataCenter':{'dataCenterId':dc_id}
                }]}

    if kp is None:
        pass
    else:
        payload['launch'][0].update({'kp':kp})

    s.post(data=json.dumps(payload))
    if s.last_error is None:
        if wait is True:
            w = wait_for_job(s.current_job)
            if w == True:
                sid = job.get(s.current_job)['message']
                return get(sid)
            else:
                return job.get(s.current_job)
        else:
            return s.current_job
    else:
        return s.last_error
