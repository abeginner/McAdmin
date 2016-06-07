import ansible.playbook
from ansible import callbacks
from ansible import utils
import json
stats = callbacks.AggregateStats()
playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
runner_cb = callbacks.PlaybookRunnerCallbacks(stats,verbose=utils.VERBOSITY)
res=ansible.playbook.PlayBook(
            inventory='192.168.134.129',
            playbook='test.yml',
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb
    ).run()
data = json.loads(res,indent=4)
print data