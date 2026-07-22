import re

with open("platform-new/src/routes/cellsentry.tsx", "r") as f:
    code = f.read()

# Replace Graph import / definition
# Find where <Graph nodes={nodes} edges={edges} /> is used
code = code.replace("<Graph nodes={nodes} edges={edges} />", "<SupplyGraph nodes={nodes} edges={edges} />")

# Import SupplyGraph
code = code.replace("""import {
  fetchGraph,""", """import { SupplyGraph } from "@/components/urja/SupplyGraph";
import {
  fetchGraph,""")

# Remove the old Graph function entirely
# Graph function starts with `function Graph({ nodes, edges }:` and goes to the end of the file.
code = re.sub(r'function Graph\(\{ nodes, edges \}: \{ nodes: GraphNode\[\]; edges: GraphEdge\[\] \}\) \{.*', '', code, flags=re.DOTALL)

with open("platform-new/src/routes/cellsentry.tsx", "w") as f:
    f.write(code)


with open("platform-new/src/lib/supply.ts", "r") as f:
    lib_code = f.read()

# Remove applyLayout completely
lib_code = re.sub(r'function applyLayout\(nodes: GraphNode\[\]\) \{.*?\n\}\n\n', '', lib_code, flags=re.DOTALL)
lib_code = lib_code.replace("applyLayout(data.nodes);\n  ", "")

with open("platform-new/src/lib/supply.ts", "w") as f:
    f.write(lib_code)

