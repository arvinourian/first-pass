from dotenv import load_dotenv
load_dotenv()
from first_pass.retrieval.index import PlaybookIndex
idx = PlaybookIndex()
idx.build(['playbooks/cleaning', 'playbooks/engineering', 'playbooks/analysis', 'playbooks/domain'])
print([pb.category for pb in idx.playbooks])
print('Domain count:', sum(1 for pb in idx.playbooks if pb.category == 'domain'))
