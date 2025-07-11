"use client";

import { PitchCraftSuite } from "@/components/dashboard/pitchcraft-suite";
import { withAuth } from "@/lib/auth-context";

function PitchCraftPage() {
  return <PitchCraftSuite />
}

export default withAuth(PitchCraftPage);


