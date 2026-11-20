import ToolAccessGate from "../components/ToolAccessGate";
import { WindCalculator } from "../components/WindCalculator";

export default function HomePage() {
  return (
    <ToolAccessGate><main>
      <WindCalculator />
    </main></ToolAccessGate>
  );
}
