import CreateDoorClient from "./CreateDoorClient";

type PageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

export default function CreateDoorPage({ searchParams = {} }: PageProps) {
  const typeRaw = searchParams.type;
  const initialType = Array.isArray(typeRaw) ? (typeRaw[0] ?? "") : (typeRaw ?? "");
  return <CreateDoorClient initialType={String(initialType)} />;
}

