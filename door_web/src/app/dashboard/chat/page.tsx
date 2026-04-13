import { AdminPage } from "@/components/dashboard/AdminPage";

export default function ChatPage() {
  return (
    <AdminPage
      eyebrow="Chat"
      title="Conversation rooms stay separate from broadcasts"
      description="Chat supports direct and group-style rooms with message state tracking. Broadcast remains separate so urgent one-way communication does not get tangled with conversational semantics."
      stats={[
        { label: "Delivery States", value: "4", tone: "teal" },
      ]}
    >
      <section className="rounded-[var(--radius-lg)] border border-[var(--line)] bg-[var(--bg-card)] p-5 text-sm leading-7 text-[var(--text-muted)]">
        This area is ready for room lists, message inspection, and delivery analytics once the admin message views are expanded.
      </section>
    </AdminPage>
  );
}
