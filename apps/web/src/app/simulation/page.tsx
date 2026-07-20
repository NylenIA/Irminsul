import type { Metadata } from "next";
import { SimulationClient } from "./SimulationClient";

export const metadata: Metadata = { title: "Simulation gcsim — Irminsul" };

export default function SimulationPage(): React.ReactElement {
  return <SimulationClient />;
}
