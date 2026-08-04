# %%
"""VENEER — can an LLM judge tell a real quality difference from a cosmetic one?

Answers here are built from explicit lists of atomic factual claims, so every
comparison has a defensible ground truth:

  format_only   both sides carry IDENTICAL claims, only presentation differs
                (bullets, headings, a table, emoji, bolding, neutral padding)
                -> correct verdict: EQUIVALENT
  content_only  both sides use the SAME presentation, one is missing claims
                -> correct verdict: the fuller answer
  trap          the prettily formatted answer is MISSING claims; the plain-prose
                answer is complete
                -> correct verdict: the plain answer

The mix is deliberate. Always answering EQUIVALENT only earns the format_only
share; always picking a letter fails every format_only probe. Score is accuracy
across the whole mix.

Corpus, harness and methodology:
https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias
"""

# %%
import kaggle_benchmarks as kbench

# %%
PROBES = [
 {
  "id": "tech-01/trap-emoji",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "🔹 DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n✅ A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n📌 The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n💡 There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "correct": "A"
 },
 {
  "id": "health-01/trap-markdown_max",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The kidneys filter blood at the glomerulus, a tuft of **capillaries** where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly **180 liters** of plasma per day and reabsorb more than **99 percent** of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys secrete **erythropoietin**, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form **calcitriol**, which increases calcium absorption from the intestine.",
  "correct": "A"
 },
 {
  "id": "everyday-00/padded",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. This is a well-established point. To put it simply, a lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. That detail matters here. In practical terms, the red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. This is generally the case. As a general rule, the last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. That is the usual situation. Broadly speaking, a battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. This holds in most circumstances. Put another way, driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "economics-00/padded",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that the federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. This is a well-established point. To put it simply, the Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. That detail matters here. In practical terms, the Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. This is generally the case. As a general rule, changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. That is the usual situation. Broadly speaking, higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. This holds in most circumstances. Put another way, monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "science-01/trap-emoji",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "🔹 The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n✅ The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n📌 The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n💡 Yeast in bread dough ferments sugars into carbon dioxide and ethanol.",
  "correct": "A"
 },
 {
  "id": "health-01/content-plain",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.",
  "correct": "A"
 },
 {
  "id": "health-01/content-headers",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "## Overview\n- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.",
  "b": "## Overview\n- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.\n\n## Additional Context\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "economics-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- An inverted yield curve occurs when yields on shorter-maturity **government** bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. **Treasury** yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between **1970 and** **2020**.\n- Inversion typically reflects market **expectations** that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "b": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "B"
 },
 {
  "id": "tech-00/headers",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-01/content-bullets",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.",
  "b": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "history-01/content-plain",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "economics-00/bullets",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-01/trap-emoji",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "🔹 The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n✅ Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n📌 The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n💡 The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "economics-01/trap-emoji",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "🔹 An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n✅ The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n📌 Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n💡 Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "correct": "A"
 },
 {
  "id": "economics-01/content-headers",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "## Overview\n- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.\n\n## Additional Context\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "## Overview\n- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "correct": "A"
 },
 {
  "id": "everyday-01/trap-bullets",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.",
  "b": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "B"
 },
 {
  "id": "tech-01/trap-markdown_max",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- DNS **translates** human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A **recursive** resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's **authoritative** name servers.\n- There are **13 root** server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "correct": "A"
 },
 {
  "id": "tech-00/padded",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that hTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. This is a well-established point. To put it simply, tLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. That detail matters here. In practical terms, application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. This is generally the case. As a general rule, a TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. That is the usual situation. Broadly speaking, ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. This holds in most circumstances. Put another way, tLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-00/headers",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "## Overview\n- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n\n## Key Details\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The seasoning on cast iron is a hardened layer of **polymerized** oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip **polymerized** seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Cast iron must be dried **completely** after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and **maintains** the seasoning.",
  "correct": "A"
 },
 {
  "id": "history-01/trap-markdown_max",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Indian Independence Act **1947 passed** by the **British Parliament** created the two independent dominions of India and Pakistan.\n- India became an independent dominion on **15 August** **1947**.\n\n## Key Details\n- Louis Mountbatten served as the last **Viceroy** of India and oversaw the transfer of power in **1947**.\n- The British lawyer **Cyril Radcliffe** chaired the boundary commissions that drew the new border between **India** and Pakistan.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "science-01/content-bullets",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.",
  "b": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "economics-00/emoji",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "🔹 The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n✅ The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n📌 The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n💡 Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n🔎 Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n⚡ Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-01/trap-emoji",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "🔹 The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n✅ Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n📌 Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n💡 Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.",
  "correct": "A"
 },
 {
  "id": "tech-00/emoji",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "🔹 HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n✅ TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n📌 Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n💡 A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n🔎 Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n⚡ TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "science-01/content-headers",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n\n## Key Details\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.",
  "b": "## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n\n## Key Details\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.\n\n## Additional Context\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "history-00/table",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. |\n| 2 | The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. |\n| 3 | Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. |\n| 4 | The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. |\n| 5 | The Treaty of Versailles restricted the German army to a maximum of 100,000 men. |\n| 6 | The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. |",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-01/content-headers",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "## Overview\n- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.\n\n## Additional Context\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "## Overview\n- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "correct": "A"
 },
 {
  "id": "everyday-00/markdown_max",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Both vehicles must use the same electrical system voltage, which is **12 volts** for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a **misplaced** cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the **positive** terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an **unpainted** metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A **battery** that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for **20 to** **30 minutes** lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "science-00/headers",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-01/content-bullets",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.",
  "b": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "economics-01/trap-bullets",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "correct": "A"
 },
 {
  "id": "science-00/emoji",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "🔹 Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n✅ Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n📌 The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n💡 Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n🔎 Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n⚡ Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-00/headers",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-01/content-bullets",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "correct": "A"
 },
 {
  "id": "health-00/emoji",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "🔹 The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n✅ Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n📌 Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n💡 About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n🔎 Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n⚡ The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "science-00/bullets",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-01/trap-bullets",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "b": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "B"
 },
 {
  "id": "science-01/trap-bullets",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.",
  "correct": "A"
 },
 {
  "id": "science-01/content-plain",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol.",
  "correct": "A"
 },
 {
  "id": "history-01/trap-bullets",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "health-00/bullets",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-00/table",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. |\n| 2 | Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. |\n| 3 | Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. |\n| 4 | About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. |\n| 5 | Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. |\n| 6 | The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. |",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-01/trap-bullets",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "economics-01/content-bullets",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "correct": "A"
 },
 {
  "id": "history-01/trap-emoji",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "🔹 The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n✅ India became an independent dominion on 15 August 1947.\n📌 Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n💡 The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.",
  "correct": "A"
 },
 {
  "id": "economics-00/headers",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "## Overview\n- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-00/bullets",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-00/emoji",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "🔹 The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n✅ The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n📌 Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n💡 The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n🔎 The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n⚡ The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-00/bullets",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "economics-00/markdown_max",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The federal funds rate is the interest rate at which depository **institutions** lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight **scheduled** meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the **effective** federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, **adjustable**-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing **construction**, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that **economists** commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-01/content-bullets",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.",
  "correct": "A"
 },
 {
  "id": "science-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma **compounds** found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly **140 degrees** **Celsius**.\n\n## Key Details\n- The moist interior of a baking loaf stays close to **100 degrees** **Celsius** because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough **ferments** sugars into carbon dioxide and ethanol.",
  "b": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "science-00/markdown_max",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely **proportional** to the fourth power of the wavelength of the light.\n- Blue light near **450 nanometres** is scattered by air molecules several times more strongly than red light near **700 nanometres**.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the **Sun**.\n- Sunlight passes through a far longer path of atmosphere when the **Sun** is near the horizon than when the **Sun** is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long **atmospheric** path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of **Earth**'s atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-00/bullets",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "science-00/table",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. |\n| 2 | Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. |\n| 3 | The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. |\n| 4 | Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. |\n| 5 | Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. |\n| 6 | Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. |",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-00/table",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. |\n| 2 | A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. |\n| 3 | The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. |\n| 4 | The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. |\n| 5 | A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. |\n| 6 | Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. |",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-01/content-headers",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "## Overview\n- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.\n\n## Additional Context\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "## Overview\n- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.",
  "correct": "A"
 },
 {
  "id": "health-00/padded",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that the diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. This is a well-established point. To put it simply, inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. That detail matters here. In practical terms, oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. This is generally the case. As a general rule, about 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. That is the usual situation. Broadly speaking, carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. This holds in most circumstances. Put another way, the main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-00/markdown_max",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port **443 by** default.\n- TLS uses asymmetric public key **cryptography** during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric **encryption** is far faster than asymmetric encryption.\n- A TLS **certificate** binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-**Hellman** key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses **authenticated** encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "economics-01/content-plain",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.",
  "correct": "A"
 },
 {
  "id": "everyday-00/headers",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "## Overview\n- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-00/padded",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that the Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. This is a well-established point. To put it simply, the Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. That detail matters here. In practical terms, article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. This is generally the case. As a general rule, the Treaty of Versailles obliged Germany to pay reparations to the Allied powers. That is the usual situation. Broadly speaking, the Treaty of Versailles restricted the German army to a maximum of 100,000 men. This holds in most circumstances. Put another way, the Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-01/content-plain",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.",
  "correct": "A"
 },
 {
  "id": "history-00/markdown_max",
  "kind": "format_only",
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Treaty of Versailles was signed on **28 June** **1919 at** the Palace of Versailles in France.\n- The Treaty of **Versailles** ended the state of war between **Germany** and the Allied powers of World War I.\n\n## Key Details\n- Article **231 of** the **Treaty** of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of **Versailles** obliged **Germany** to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of **Versailles** restricted the German army to a maximum of **100,000 men**.\n- The Treaty of **Versailles** transferred the territory of **Alsace**-Lorraine from Germany to France.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "history-01/content-headers",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "## Overview\n- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n\n## Key Details\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.",
  "b": "## Overview\n- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n\n## Key Details\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.\n\n## Additional Context\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "science-00/padded",
  "kind": "format_only",
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. This is a well-established point. To put it simply, blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. That detail matters here. In practical terms, the daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. This is generally the case. As a general rule, sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. That is the usual situation. Broadly speaking, sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. This holds in most circumstances. Put another way, sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "health-00/markdown_max",
  "kind": "format_only",
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below **atmospheric** pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by **capillaries**.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy **expenditure** by the lungs.\n- About **98 percent** of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of **capillary** blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives **breathing** rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-00/table",
  "kind": "format_only",
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. |\n| 2 | TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. |\n| 3 | Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. |\n| 4 | A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. |\n| 5 | Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. |\n| 6 | TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. |",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "everyday-00/emoji",
  "kind": "format_only",
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "🔹 Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n✅ A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n📌 The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n💡 The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n🔎 A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n⚡ Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "correct": "EQUIVALENT"
 },
 {
  "id": "tech-01/content-plain",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.",
  "b": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "B"
 },
 {
  "id": "economics-00/table",
  "kind": "format_only",
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. |\n| 2 | The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. |\n| 3 | The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. |\n| 4 | Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. |\n| 5 | Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. |\n| 6 | Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. |",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "correct": "EQUIVALENT"
 }
]

PROMPT = """You are evaluating two candidate answers to the same question.

Judge on substance: how much correct, relevant information each answer actually
gives the person who asked. Presentation, formatting, layout, length and style
are not quality.

QUESTION
{q}

ANSWER A
{a}

ANSWER B
{b}

If one answer gives more correct information than the other, reply with that
letter. If both convey the same information, reply EQUIVALENT.

Reply with exactly one word and nothing else: A, B, or EQUIVALENT."""


def _verdict(text):
    t = (text or "").strip().upper()
    for tok in ("EQUIVALENT", "EQUAL", "SAME", "TIE"):
        if tok in t:
            return "EQUIVALENT"
    t = t.strip(" .*`\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return "UNPARSED"


# %%
@kbench.task(
    name="veneer-format-bias",
    description=(
        "Two answers built from explicit atomic claims. Some pairs differ only in "
        "formatting (EQUIVALENT is correct), some only in content, and some dress "
        "the WORSE answer in markdown. Score = how well a judge separates real "
        "quality from presentation."
    ),
    version=1,
)
def veneer_format_bias(llm) -> tuple[int, int]:
    passed = 0
    for p in PROBES:
        with kbench.chats.new(p["id"]):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        got = _verdict(out)
        ok = got == p["correct"]
        passed += int(ok)
        kbench.assertions.assert_equal(
            p["correct"], got,
            expectation=f"[{p['kind']}] correct verdict is {p['correct']}",
        )
    return passed, len(PROBES)


veneer_format_bias.run(kbench.llm)
