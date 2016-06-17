from django.db import models
from django.contrib.auth.models import AbstractBaseUser,  BaseUserManager
from McAdmin.mcadmin.backends import CmdbBackend



class IdcManager(models.Manager):
    pass

class Idc(models.Model):
    idc_id = models.IntegerField(primary_key=True)
    idc_code = models.IntegerField(unique=True, db_index=True)
    idc_fullname =  models.CharField(max_length=40)
    
    object = IdcManager()
    
    class Meta:
        db_table = 'cmdb_idc'
    
    def __unicode__(self):
        return self.idc_fullname


class OsTypeManager(models.Manager):
    pass

class OsType(models.Model):
    ostype_id = models.IntegerField(primary_key=True)
    ostype_code = models.IntegerField(unique=True, db_index=True)
    ostype_fullname = models.CharField(max_length=40)
    
    object = OsTypeManager()
    
    class Meta:
        db_table = 'cmdb_ostype'
    
    def __unicode__(self):
        return self.os_fullname


class StaffManager(models.Manager):
    pass

class Staff(models.Model):
    staff_id = models.IntegerField(primary_key=True)
    staff_code = models.CharField(max_length=10, unique=True, db_index=True)
    staff_passport = models.CharField(max_length=40, unique=True, db_index=True)
    staff_fullname = models.CharField(max_length=40)
    
    object = StaffManager()
    
    class Meta:
        db_table = 'cmdb_staff'
    
    def __unicode__(self):
        return self.staff_fullname


class BussinessManager(models.Manager):
    pass

class Bussiness(models.Model):
    bussiness_id = models.IntegerField(primary_key=True)
    bussiness_code = models.IntegerField(unique=True, db_index=True)
    bussiness_fullname = models.CharField(max_length=100, unique=True, db_index=True)
    
    object = BussinessManager()
    
    class Meta:
        db_table = 'cmdb_bussiness'
    
    def __unicode__(self):
        return self.bussiness_fullname


class ServerTypeManager(models.Manager):
    pass

class ServerType(models.Model):
    servertype_id = models.IntegerField(primary_key=True)
    servertype_code = models.IntegerField(unique=True, db_index=True)
    servertype_fullname = models.CharField(max_length=20)

    object = ServerTypeManager()
    
    class Meta:
        db_table = 'cmdb_servertype'

    def __unicode__(self):
        return self.servertype_fullname


class StatusManager(models.Manager):
    pass

class Status(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_code = models.IntegerField(unique=True, db_index=True)
    status_fullname = models.CharField(max_length=20)

    object = StatusManager()
    
    class Meta:
        db_table = 'cmdb_status'
    
    def __unicode__(self):
        return self.status_fullname


class ServerManager(models.Manager):
    pass

class Server(models.Model):
    server_id = models.IntegerField(primary_key=True)
    server_code = models.IntegerField(unique=True, db_index=True)
    asset_tag = models.CharField(max_length=25)
    idc = models.ForeignKey(Idc)
    os = models.ForeignKey(OsType)
    tech_admin = models.CharField(max_length=40)
    sysop_admin = models.CharField(max_length=40)
    server_type = models.ForeignKey(ServerType)
    status = models.ForeignKey(Status)
    bussiness = models.ManyToManyField(Bussiness, null=True)

    object = ServerManager()
    
    class Meta:
        db_table = 'cmdb_server'


class IspManager(models.Manager):
    pass

class Isp(models.Model):
    isp_id = models.IntegerField(primary_key=True)
    isp_code = models.IntegerField(max_length=10)
    isp_shortname = models.CharField(max_length=20, db_index=True, unique=True)
    isp_fullname = models.CharField(max_length=20, db_index=True, unique=True)
    
    object = IspManager()
    
    class Meta:
        db_table = 'cmdb_isp'
    
    def __unicode__(self):
        return self.isp_fullname


class IpAddressManager(models.Manager):
    pass

class IpAddress(models.Model):
    ipaddress_id = models.IntegerField(primary_key=True)
    server = models.ForeignKey(Server, null=True)
    isp = models.ForeignKey(Isp, null=True)
    idc = models.ForeignKey(Idc, null=True)
    ipaddress = models.GenericIPAddressField(unique=True, db_index=True)

    object = IpAddressManager()
    
    class Meta:
        db_table = 'cmdb_ipaddress'
        verbose_name = "ipaddress"
    
    def __unicode__(self):
        return self.ipaddress
    

class MemcacheHostManager(models.Manager):
    pass

class MemcacheHost(models.Model):
    memcachehost_id = models.IntegerField(primary_key=True)
    server_code = models.IntegerField(unique=True, db_index=True)
    interip = models.IPAddressField(unique=True, db_index=True)
    status = models.IntegerField()
    version = models.CharField(max_length=18)
    idc_code = models.IntegerField()
    idc_fullname = models.CharField(max_length=40)
    description = models.CharField(max_length=200, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    object = MemcacheHostManager()
    
    class Meta:
        db_table = 'mcadmin_memcachehost'
    
    def __unicode__(self):
        return self.description
    

class MemcacheAgentManager(models.Manager):
    pass

class MemcacheAgent(models.Model):
    agent_id = models.IntegerField(primary_key=True)
    agent_code = models.IntegerField(unique=True, db_index=True)
    server_id = models.IntegerField()
    node = models.GenericIPAddressField()
    bind_host = models.GenericIPAddressField()
    bind_port = models.IntegerField()
    pool_size = models.IntegerField()
    idc_code = models.IntegerField(unique=True, db_index=True)
    application = models.CharField(max_length=30)
    paste_conf = models.CharField(max_length=30)
    
    object = MemcacheAgentManager()
    
    class Meta:
        db_table = 'mcadmin_memcacheagent'


class IdcMirrorManager(models.Manager):
    pass

class IdcMirror(models.Model):
    idc_id = models.IntegerField(primary_key=True)
    idc_code = models.IntegerField(unique=True, db_index=True)
    idc_fullname =  models.CharField(max_length=40)
    
    object = IdcManager()
    
    class Meta:
        db_table = 'cmdb_idc_mirror'
    
    def __unicode__(self):
        return self.idc_fullname


class MemcacheBussinessManager(models.Manager):
    pass

class MemcacheBussiness(models.Model):
    bussiness_id = models.IntegerField(primary_key=True)
    bussiness_code = models.IntegerField(unique=True, db_index=True)
    bussiness_shortname = models.CharField(max_length=30, unique=True, db_index=True)
    bussiness_fullname = models.CharField(max_length=100, unique=True, db_index=True)
    
    object = MemcacheBussinessManager()
    
    class Meta:
        db_table = 'mcadmin_memcachebussiness'
    
    def __unicode__(self):
        return self.bussiness_fullname


class MemcacheSubsystemManager(models.Manager):
    pass

class MemcacheSubsystem(models.Model):
    subsystem_id = models.IntegerField(primary_key=True)
    subsystem_code = models.IntegerField(unique=True, db_index=True)
    bussiness = models.ForeignKey(MemcacheBussiness)
    subsystem_fullname = models.CharField(max_length=100)
    
    object = MemcacheBussinessManager()
    
    class Meta:
        db_table = 'mcadmin_memcachesubsystem'
    
    def __unicode__(self):
        return self.subsystem_fullname


class MemcacheGroupManager(models.Manager):
    pass

class MemcacheGroup(models.Model):
    group_id = models.IntegerField(primary_key=True)
    group_code = models.IntegerField(unique=True, db_index=True)
    subsystem = models.ForeignKey(MemcacheSubsystem)
    group_name = models.CharField(max_length=60)
    
    object = MemcacheAgentManager()
    
    class Meta:
        db_table = 'mcadmin_memcachegroup'
    
    def __unicode__(self):
        return self.group_name
    

class MemcacheInstanceManager(models.Manager):
    pass

class MemcacheInstance(models.Model):
    instance_id = models.IntegerField(primary_key=True)
    instance_code = models.IntegerField(unique=True, db_index=True)
    host = models.ForeignKey(MemcacheHost)
    group = models.ForeignKey(MemcacheGroup)
    port = models.IntegerField()
    max_memory = models.IntegerField()
    max_connection = models.IntegerField()
    is_bind = models.BooleanField()
    tech_admin = models.CharField(max_length=20)
    sysop_admin = models.CharField(max_length=20)
    creator = models.CharField(max_length=20)
    status = models.IntegerField()
    md5_sum = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
    
    object = MemcacheInstanceManager()
    
    class Meta:
        db_table = 'mcadmin_memcacheinstance'
        unique_together = (("host", "port"),)
    
    def __unicode__(self):
        return self.name


class UserManager(BaseUserManager):
    pass

class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    yyuid = models.CharField(max_length=15)
    realname = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField()
    department = models.CharField(max_length=60)
    
    USERNAME_FIELD = 'username'
    
    object = UserManager()
    
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.username
    
    def is_authenticated(self):
        return True

    class Meta:
        db_table = 'mcadmin_user'
    
    def __unicode__(self):
        return self.username




