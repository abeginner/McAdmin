from django.db import models


class IdcManager(models.Manager):
    pass

class Idc(models.Model):
    idc_id = models.IntegerField()
    idc_fullname =  models.CharField(max_length=40)
    
    object = IdcManager()
    
    def __unicode__(self):
        return self.idc_fullname


class OsManager(models.Manager):
    pass

class Os(models.Model):
    os_id = models.IntegerField()
    os_fullname = models.CharField(max_length=40)
    
    object = OsManager()
    
    def __unicode__(self):
        return self.os_fullname


class StaffManager(models.Manager):
    pass

class Staff(models.Model):
    staff_id = os_id = models.IntegerField()
    staff_passport = models.CharField(max_length=40)
    staff_fullname = models.CharField(max_length=40)
    
    object = StaffManager()
    
    def __unicode__(self):
        return self.staff_fullname


class BussinessManager(models.Manager):
    pass

class Bussiness(models.Model):
    bussiness_id = models.IntegerField()
    bussiness_fullname = models.CharField(max_length=100)
    
    object = BussinessManager()
    
    def __unicode__(self):
        return self.bussiness_fullname


class ServerTypeManager(models.Manager):
    pass

class ServerType(models.Model):
    server_type_id = models.IntegerField()
    server_type_fullname = models.CharField(max_length=20)

    object = ServerTypeManager()

    def __unicode__(self):
        return self.server_type_fullname


class StatusManager(models.Manager):
    pass

class Status(models.Model):
    status_id = models.IntegerField()
    status_fullname = models.CharField(max_length=20)

    object = StatusManager()
    
    def __unicode__(self):
        return self.status_fullname


class ServerManager(models.Manager):
    pass

class Server(models.Model):
    server_id = models.IntegerField()
    idc = models.ForeignKey(Idc)
    os = models.ForeignKey(Os)
    tech_admin = models.ForeignKey(Staff)
    sysop_admin = models.ForeignKey(Staff)
    server_type = models.ForeignKey(ServerType)
    status = models.ForeignKey(Status)
    bussiness = models.ManyToManyField(Bussiness)

    object = ServerManager()
    
    def __unicode__(self):
        pass


class IspManager(models.Manager):
    pass

class Isp(models.Model):
    isp_id = models.IntegerField()
    isp_fullname = models.CharField(max_length=20, unique=True)
    
    object = IspManager()
    
    def __unicode__(self):
        return self.isp_fullname


class IpAddressManager(models.Manager):
    pass

class IpAddress(models.Model):
    ipaddress_id = models.IntegerField(unique=True)
    server = models.ForeignKey(Server)
    ipaddress = models.GenericIPAddressField(unique=True)

    object = IpAddressManager()
    
    def __unicode__(self):
        return self.ipaddress


class MemcacheHostManager(models.Manager):
    pass

class MemcacheHost(models.Model):
    server_id = models.IntegerField()
    interip = models.IPAddressField(unique=True)
    version = models.CharField(max_length=18)
    idc = models.ForeignKey(Idc)
    description = models.CharField(max_length=100, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    object = MemcacheHostManager()
    
    def __unicode__(self):
        return self.description
    

class MemcacheAgentManager(models.Manager):
    pass

class MemcacheAgent(models.Model):
    server_id = models.IntegerField()
    node = models.GenericIPAddressField()
    bind_host = models.GenericIPAddressField()
    bind_port = models.IntegerField()
    pool_size = models.IntegerField()
    idc_id = models.IntegerField()
    application = models.CharField(max_length=30)
    paste_conf = models.CharField(max_length=30)
    
    object = MemcacheAgentManager()
    
    def __unicode__(self):
        pass


class MemcacheGroupManager(models.Manager):
    pass

class MemcacheGroup(models.Model):
    group_id = models.IntegerField()
    bussiness_id = models.IntegerField()
    group_name = models.CharField(max_length=60)
    
    object = MemcacheAgentManager()
    
    def __unicode__(self):
        return self.group_name


class InstanceManager(models.Manager):
    pass

class Instance(models.Model):
    instance_id = models.IntegerField()
    host = models.ForeignKey(MemcacheHost)
    group = models.ForeignKey(MemcacheGroup)
    port = models.IntegerField()
    max_memory = models.IntegerField()
    max_connection = models.IntegerField()
    is_bind = models.BooleanField()
    tech_admin = models.CharField(max_length=20)
    sys_admin = models.CharField(max_length=20)
    creator = models.CharField(max_length=20)
    status = models.IntegerField()
    md5_sum = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
    
    object = InstanceManager()
    
    def __unicode__(self):
        return self.name














