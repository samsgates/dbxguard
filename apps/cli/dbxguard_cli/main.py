from __future__ import annotations
import json,subprocess
from pathlib import Path
import httpx,typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dbxguard_connectors.databricks import DatabricksConnector
from dbxguard_core.analyzer import Analyzer
from dbxguard_core.graph import DependencyGraph
from dbxguard_core.models import GraphEdge,GraphNode
from dbxguard_parsers.bundle import diff_bundle,load_yaml
from dbxguard_parsers.sql import parse_sql_file
from dbxguard_parsers.terraform import parse_terraform_file
from dbxguard_policy.engine import PolicyEngine
app=typer.Typer(help="DBXGuard. Pre-flight change intelligence for Databricks."); console=Console()
def _graph(path:Path)->DependencyGraph:
    data=json.loads(path.read_text()); graph=DependencyGraph()
    for node in data["nodes"]: graph.add_node(GraphNode(**node))
    for edge in data["edges"]: graph.add_edge(GraphEdge(**edge))
    return graph
def _show(result,json_output:bool=False):
    if json_output: console.print(result.model_dump_json(indent=2)); return
    console.print(Panel.fit(f"[bold]{result.decision.value}[/bold]\nRisk {result.risk.score}/100 · {result.risk.severity.value}\nConfidence {result.risk.confidence:.0%}",title="DBXGuard"))
    table=Table("Category","Severity","Resource","Finding")
    for f in result.findings: table.add_row(f.category,f.severity.value,f.resource,f.title)
    console.print(table); console.print(f"Blast radius: {result.impact.total} asset(s). Critical: {len(result.impact.critical_assets)}")
@app.command()
def demo(json_output:bool=typer.Option(False,"--json")):
    root=Path(__file__).resolve().parents[3]; graph=_graph(root/"examples/demo/graph.json"); base=json.loads((root/"examples/demo/base_schema.json").read_text()); changes=parse_sql_file(root/"examples/demo/change.sql",base); policy=PolicyEngine.from_directory(root/"policies"); _show(Analyzer(graph,policy).analyze(changes,"production"),json_output)
@app.command("analyze")
def analyze_file(file:Path,environment:str=typer.Option("development","--environment","-e"),base_schema:Path|None=typer.Option(None,"--base-schema"),graph_file:Path|None=typer.Option(None,"--graph"),json_output:bool=typer.Option(False,"--json")):
    graph=_graph(graph_file) if graph_file else DependencyGraph(); policy=PolicyEngine.from_directory("policies") if Path("policies").exists() else PolicyEngine([])
    if file.suffix.lower()==".sql": changes=parse_sql_file(file,json.loads(base_schema.read_text()) if base_schema else {})
    elif file.suffix.lower()==".tf": changes=parse_terraform_file(file)
    else: raise typer.BadParameter("Supported files: .sql, .tf")
    _show(Analyzer(graph,policy).analyze(changes,environment),json_output)
@app.command("bundle-diff")
def bundle_diff(before:Path,after:Path,environment:str="development",json_output:bool=False): _show(Analyzer().analyze(diff_bundle(load_yaml(before),load_yaml(after),str(after)),environment),json_output)
@app.command("git-diff")
def git_diff(base:str="main",environment:str="development"):
    files=subprocess.check_output(["git","diff","--name-only",f"{base}...HEAD"],text=True).splitlines(); changes=[]
    for name in files:
        p=Path(name)
        if not p.exists(): continue
        if p.suffix==".sql": changes.extend(parse_sql_file(p))
        elif p.suffix==".tf": changes.extend(parse_terraform_file(p))
    result=Analyzer(policy_engine=PolicyEngine.from_directory("policies") if Path("policies").exists() else PolicyEngine([])).analyze(changes,environment); _show(result); raise typer.Exit(code=2 if result.decision.value=="BLOCK" else 0)
@app.command("policy-test")
def policy_test(directory:Path=Path("policies")):
    engine=PolicyEngine.from_directory(directory); console.print(f"Loaded {len(engine.policies)} policy document(s) from {directory}")
    for policy in engine.policies: console.print(f"[green]✓[/green] {policy.get('metadata',{}).get('name',policy.get('__file__','unnamed'))}")
@app.command("workspace-test")
def workspace_test(): console.print_json(data=DatabricksConnector().test_connection())
@app.command("workspace-capabilities")
def workspace_capabilities(): console.print_json(data=DatabricksConnector().discover_capabilities().__dict__)
@app.command("api-analyze")
def api_analyze(file:Path,api_url:str="http://localhost:8080",environment:str="development"):
    if file.suffix!=".sql": raise typer.BadParameter("api-analyze accepts SQL files")
    resp=httpx.post(f"{api_url}/api/v1/analyses/sql",json={"environment":environment,"sql":file.read_text()},timeout=60); resp.raise_for_status(); console.print_json(data=resp.json())
if __name__=="__main__": app()
