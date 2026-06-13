// Renders a JSON-LD script tag into the document head via react-helmet-async.
import { Helmet } from "react-helmet-async";

interface JsonLdProps {
  graph: Record<string, unknown>;
}

export default function JsonLd({ graph }: JsonLdProps) {
  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(graph)}
      </script>
    </Helmet>
  );
}
