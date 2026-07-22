import re

with open("platform-new/src/routes/cellsentry.tsx", "r") as f:
    code = f.read()

# 1. Update the grid layout
code = code.replace(
    """<div className="grid gap-6 xl:grid-cols-[280px_1fr_300px]">""",
    """<div className="grid gap-6 xl:grid-cols-[1fr_2fr_1fr] h-[640px]">"""
)

# 2. Update Left Card (Signal Feed)
left_card_old = """<GlassCard padding="md">
          <div className="mb-3 text-[15px] font-semibold">Signal Feed</div>
          <div className="flex flex-col gap-2">"""
left_card_new = """<GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 text-[15px] font-semibold shrink-0">Signal Feed</div>
          <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-2 custom-scrollbar">"""
code = code.replace(left_card_old, left_card_new)

# 3. Update Center Card (Knowledge Graph)
center_card_old = """<GlassCard padding="md">
          <div className="mb-3 flex items-center justify-between">"""
center_card_new = """<GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 flex items-center justify-between shrink-0">"""
code = code.replace(center_card_old, center_card_new)

center_graph_old = """</div>
          <div className="relative">"""
center_graph_new = """</div>
          <div className="relative flex-1 min-h-0">"""
code = code.replace(center_graph_old, center_graph_new)

# 4. Update Right Card (Alerts)
right_card_old = """<GlassCard padding="md">
          <div className="mb-3 text-[15px] font-semibold">Risk Alerts</div>"""
right_card_new = """<GlassCard padding="md" className="flex flex-col h-full overflow-hidden">
          <div className="mb-3 text-[15px] font-semibold shrink-0">Risk Alerts</div>"""
code = code.replace(right_card_old, right_card_new)

alerts_old = """{!loading && alerts.length > 0 && (
            <div className="flex flex-col gap-2">"""
alerts_new = """{!loading && alerts.length > 0 && (
            <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-2 custom-scrollbar">"""
code = code.replace(alerts_old, alerts_new)


with open("platform-new/src/routes/cellsentry.tsx", "w") as f:
    f.write(code)
