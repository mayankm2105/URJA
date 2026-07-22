import { useState, type ReactNode } from "react";
import { PageShell, PageHeader } from "@/components/urja/PageShell";
import { RightTabRail, type TabItem } from "@/components/urja/RightTabRail";

export function AgentPage({
  agentName,
  eyebrow,
  mission,
  tabs,
  renderContent,
  initialTab,
}: {
  agentName: string;
  eyebrow: string;
  mission: string;
  tabs: TabItem[];
  renderContent: (activeKey: string) => ReactNode;
  initialTab?: string;
}) {
  const [active, setActive] = useState(initialTab || tabs[0]?.key || "");
  return (
    <PageShell orbs="subtle">
      <div className="mx-auto max-w-[1440px] px-6 py-12">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-8 mb-2">
          <div className="flex-1">
            <PageHeader eyebrow={eyebrow} title={agentName} subtitle={mission} />
          </div>
          <div className="shrink-0 lg:mt-0 mt-4">
            <RightTabRail
              items={tabs}
              active={active}
              onChange={setActive}
              agentName={agentName}
            />
          </div>
        </div>
        <main className="min-w-0">{renderContent(active)}</main>
      </div>
    </PageShell>
  );
}
