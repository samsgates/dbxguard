from dbxguard_core.analyzer import Analyzer
from dbxguard_core.graph import DependencyGraph
from dbxguard_core.models import Change,ChangeOperation,Decision,GraphEdge,GraphNode,ResourceType
from dbxguard_policy.engine import PolicyEngine

def test_blast_radius_and_block():
    graph=DependencyGraph(); graph.add_node(GraphNode(id="a.col",name="col",type=ResourceType.COLUMN)); graph.add_node(GraphNode(id="job.critical",name="job",type=ResourceType.JOB,criticality=0)); graph.add_edge(GraphEdge(source="a.col",target="job.critical"))
    change=Change(resource="a.col",resource_type=ResourceType.COLUMN,operation=ChangeOperation.DROP_COLUMN)
    policy=PolicyEngine([{"metadata":{"name":"block-drop"},"spec":{"match":{"environment":"production"},"rules":[{"condition":{"operation":"DROP_COLUMN"},"action":"BLOCK"}]}}])
    result=Analyzer(graph,policy).analyze([change],"production"); assert result.impact.total==1; assert result.decision==Decision.BLOCK; assert result.risk.score>=20
