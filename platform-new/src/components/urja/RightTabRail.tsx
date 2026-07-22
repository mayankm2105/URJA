import type { LucideIcon } from "lucide-react";

export type TabItem = {
  key: string;
  label: string;
  icon: LucideIcon;
  desc?: string;
};

export function RightTabRail({
  items,
  active,
  onChange,
  agentName,
}: {
  items: TabItem[];
  active: string;
  onChange: (k: string) => void;
  agentName: string;
}) {
  return (
    <aside
      className="glass sticky top-24 hidden h-fit w-[280px] shrink-0 rounded-[20px] p-3 lg:block"
    >
      <div className="mb-3 px-3 pt-2">
        <div className="eyebrow">Agent</div>
        <div className="mt-1 text-[15px] font-semibold">{agentName}</div>
      </div>
      <div className="flex flex-col gap-1">
        {items.map((it) => {
          const isActive = it.key === active;
          const Icon = it.icon;
          return (
            <button
              key={it.key}
              onClick={() => onChange(it.key)}
              className="relative flex h-12 items-center gap-3 rounded-[12px] px-4 text-left transition-colors"
              style={{
                background: isActive ? "rgba(91,95,237,0.12)" : "transparent",
                color: isActive ? "#7b7fff" : "var(--color-text-secondary)",
                fontWeight: isActive ? 500 : 400,
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = "rgba(255,255,255,0.04)";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = "transparent";
              }}
            >
              {isActive && (
                <span
                  className="absolute left-0 top-2 bottom-2 w-[3px] rounded-full"
                  style={{ background: "#5b5fed" }}
                />
              )}
              <Icon className="h-4 w-4" />
              <span className="text-[14px]">{it.label}</span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
