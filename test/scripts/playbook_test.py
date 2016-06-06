import ansible.runner

runner = ansible.runner.Runner(
  module_name='test.yml',
  is_playbook=True,
  module_args='',
  remote_user='lijie',
  remote_pass='123456'
)