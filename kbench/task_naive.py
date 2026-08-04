# %%
"""VENEER (naive rubric) - does an LLM judge ignore formatting BY DEFAULT?\n\nThe prompt is written the way real eval harnesses write it: 'Which response is better? Reply A or B.' No tie option, no guidance about formatting.\n\nOnly probes with an unambiguous correct answer are scored: content_only (one side is missing claims) and trap (the prettily formatted answer is the one missing claims). Pairs that differ ONLY in formatting have no correct answer under a forced choice, so they are excluded rather than scored against an invented criterion.\n\nThe per-model difference from veneer-format-bias is how much a judge loses purely because nobody told it to look past presentation.\n\nhttps://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias"""

# %%
import kaggle_benchmarks as kbench

# %%
PROBES = [
 {
  "id": "tech-01/trap-bullets",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "B"
 },
 {
  "id": "everyday-01/trap-bullets",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "B"
 },
 {
  "id": "history-01/trap-bullets",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "science-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma **compounds** found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly **140 degrees** **Celsius**.\n\n## Key Details\n- The wheat **proteins** glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly **60 to** **70 degrees** Celsius during baking, which sets the structure of the crumb.",
  "b": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "tech-01/content-headers",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "## Overview\n- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "## Overview\n- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.\n\n## Additional Context\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "B"
 },
 {
  "id": "tech-01/content-bullets",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers.\n- There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing.\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "- DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n- Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "A"
 },
 {
  "id": "science-01/trap-emoji",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "🔹 The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n✅ The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n📌 The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n💡 Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "A"
 },
 {
  "id": "health-01/trap-markdown_max",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The kidneys filter blood at the glomerulus, a tuft of **capillaries** where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly **180 liters** of plasma per day and reabsorb more than **99 percent** of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces **angiotensin** II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming **bicarbonate** from the filtrate.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "health-01/content-headers",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "## Overview\n- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "## Overview\n- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n\n## Key Details\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.\n\n## Additional Context\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "tech-01/trap-emoji",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "🔹 DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n✅ A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n📌 Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached.\n💡 An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "A"
 },
 {
  "id": "history-01/content-plain",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "A"
 },
 {
  "id": "everyday-01/trap-emoji",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "🔹 The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n✅ Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n📌 Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n💡 Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "A"
 },
 {
  "id": "science-01/content-bullets",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "A"
 },
 {
  "id": "tech-01/trap-markdown_max",
  "kind": "trap",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- DNS **translates** human-readable domain names into the IP addresses that routers and hosts use to deliver packets.\n- A **recursive** resolver performs the chain of lookups on behalf of a client and returns a single final answer.\n\n## Key Details\n- Every DNS record carries a time-to-live value that tells **resolvers** how many seconds they may keep the answer cached.\n- An A record maps a name to an IPv4 **address** while an AAAA record maps a name to an IPv6 address.",
  "b": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "B"
 },
 {
  "id": "science-01/content-headers",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n\n## Key Details\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "## Overview\n- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n\n## Key Details\n- The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning.\n- Yeast in bread dough ferments sugars into carbon dioxide and ethanol.\n\n## Additional Context\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "health-01/trap-bullets",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "B"
 },
 {
  "id": "economics-01/content-plain",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "A"
 },
 {
  "id": "economics-01/trap-bullets",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "B"
 },
 {
  "id": "history-01/trap-emoji",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "🔹 The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n✅ India became an independent dominion on 15 August 1947.\n📌 The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n💡 The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "A"
 },
 {
  "id": "science-01/content-plain",
  "kind": "content_only",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "A"
 },
 {
  "id": "tech-01/content-plain",
  "kind": "content_only",
  "q": "What actually happens during a DNS lookup when a browser needs to reach a website?",
  "a": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. The DNS namespace is a hierarchy in which root servers refer queries to top-level domain servers, which in turn refer them to a domain's authoritative name servers. There are 13 root server address sets labeled A through M, each of which is served by many physical machines using anycast routing. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "b": "DNS translates human-readable domain names into the IP addresses that routers and hosts use to deliver packets. A recursive resolver performs the chain of lookups on behalf of a client and returns a single final answer. Every DNS record carries a time-to-live value that tells resolvers how many seconds they may keep the answer cached. An A record maps a name to an IPv4 address while an AAAA record maps a name to an IPv6 address.",
  "correct": "A"
 },
 {
  "id": "everyday-01/content-headers",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "## Overview\n- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "## Overview\n- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.\n\n## Additional Context\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "B"
 },
 {
  "id": "economics-01/content-bullets",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "A"
 },
 {
  "id": "health-01/content-plain",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "A"
 },
 {
  "id": "everyday-01/content-plain",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "A"
 },
 {
  "id": "everyday-01/content-bullets",
  "kind": "content_only",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron.\n- Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning.\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "b": "- The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago.\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "A"
 },
 {
  "id": "history-01/trap-markdown_max",
  "kind": "trap",
  "q": "How was British India partitioned in 1947?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Indian Independence Act **1947 passed** by the **British Parliament** created the two independent dominions of India and Pakistan.\n- India became an independent dominion on **15 August** **1947**.\n\n## Key Details\n- The Radcliffe Line divided the provinces of **Punjab** and **Bengal** between India and Pakistan.\n- The partition of **British India** was accompanied by mass migration and communal violence across the new borders in **Punjab** and Bengal.",
  "b": "The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan. India became an independent dominion on 15 August 1947. Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947. The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan. The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan. The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "economics-01/trap-emoji",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "🔹 An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n✅ The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n📌 The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n💡 An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "A"
 },
 {
  "id": "everyday-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is the right way to clean and care for a cast iron skillet?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The seasoning on cast iron is a hardened layer of **polymerized** oil chemically bonded to the metal, not loose oil resting on the surface.\n- Small amounts of mild dish soap will not strip **polymerized** seasoning from cast iron, unlike the lye-based soaps of a century ago.\n\n## Key Details\n- Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the **seasoning** layer and give food a metallic taste.\n- Rust on cast iron can be scoured off with steel wool, after which the pan is re-**seasoned** by baking it with a very thin layer of oil.",
  "b": "The seasoning on cast iron is a hardened layer of polymerized oil chemically bonded to the metal, not loose oil resting on the surface. Small amounts of mild dish soap will not strip polymerized seasoning from cast iron, unlike the lye-based soaps of a century ago. Cast iron must be dried completely after washing because standing water causes rust to form on exposed iron. Wiping a thin coat of cooking oil onto a dry cast iron pan protects the surface from moisture and maintains the seasoning. Simmering highly acidic foods such as tomato sauce for long periods can dissolve part of the seasoning layer and give food a metallic taste. Rust on cast iron can be scoured off with steel wool, after which the pan is re-seasoned by baking it with a very thin layer of oil.",
  "correct": "B"
 },
 {
  "id": "health-01/trap-emoji",
  "kind": "trap",
  "q": "What do the kidneys actually do in the body?",
  "a": "The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind. Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream. The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells. The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine. The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone. The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "🔹 The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n✅ Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n📌 The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n💡 The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "A"
 },
 {
  "id": "health-01/content-bullets",
  "kind": "content_only",
  "q": "What do the kidneys actually do in the body?",
  "a": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys secrete erythropoietin, a hormone that signals the bone marrow to produce red blood cells.\n- The kidneys convert vitamin D into its active form calcitriol, which increases calcium absorption from the intestine.\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "b": "- The kidneys filter blood at the glomerulus, a tuft of capillaries where blood pressure pushes water and small solutes into the nephron while blood cells and most proteins stay behind.\n- Human kidneys filter roughly 180 liters of plasma per day and reabsorb more than 99 percent of that fluid back into the bloodstream.\n- The kidneys help regulate blood pressure by releasing the enzyme renin, which starts the cascade that produces angiotensin II and aldosterone.\n- The kidneys maintain acid-base balance by excreting hydrogen ions into the urine and reclaiming bicarbonate from the filtrate.",
  "correct": "A"
 },
 {
  "id": "science-01/trap-bullets",
  "kind": "trap",
  "q": "What is actually happening chemically when bread bakes, and why does the crust brown while the inside stays pale?",
  "a": "- The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust.\n- The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius.\n- The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked.\n- Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "b": "The Maillard reaction between amino acids and reducing sugars produces the brown pigments and many of the aroma compounds found in baked bread crust. The Maillard reaction becomes rapid at temperatures above roughly 140 degrees Celsius. The moist interior of a baking loaf stays close to 100 degrees Celsius because evaporating water absorbs heat, which keeps the crumb from browning. Yeast in bread dough ferments sugars into carbon dioxide and ethanol. The wheat proteins glutenin and gliadin form an elastic gluten network that traps gas bubbles once flour is hydrated and worked. Wheat starch granules absorb water and gelatinize at roughly 60 to 70 degrees Celsius during baking, which sets the structure of the crumb.",
  "correct": "B"
 },
 {
  "id": "history-01/content-headers",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "## Overview\n- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n\n## Key Details\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "## Overview\n- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n\n## Key Details\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.\n\n## Additional Context\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "B"
 },
 {
  "id": "economics-01/content-headers",
  "kind": "content_only",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "## Overview\n- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "## Overview\n- An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020.\n- Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation.\n\n## Additional Context\n- The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "B"
 },
 {
  "id": "economics-01/trap-markdown_max",
  "kind": "trap",
  "q": "What is an inverted yield curve and why do investors pay attention to it?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- An inverted yield curve occurs when yields on shorter-maturity **government** bonds exceed yields on longer-maturity bonds.\n- The spread between the ten-year and two-year U.S. **Treasury** yields is one of the most commonly cited measures of yield curve inversion.\n\n## Key Details\n- The **historical** lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years.\n- An inverted curve **compresses** the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "b": "An inverted yield curve occurs when yields on shorter-maturity government bonds exceed yields on longer-maturity bonds. The spread between the ten-year and two-year U.S. Treasury yields is one of the most commonly cited measures of yield curve inversion. Inversion of the U.S. Treasury yield curve preceded every U.S. recession that began between 1970 and 2020. Inversion typically reflects market expectations that the central bank will cut short-term rates in the future in response to weaker growth or lower inflation. The historical lag between the onset of an inversion and the start of a recession has ranged from roughly six months to two years. An inverted curve compresses the margin banks earn from borrowing at short maturities and lending at long maturities, which can tighten the supply of credit.",
  "correct": "B"
 },
 {
  "id": "history-01/content-bullets",
  "kind": "content_only",
  "q": "How was British India partitioned in 1947?",
  "a": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- Louis Mountbatten served as the last Viceroy of India and oversaw the transfer of power in 1947.\n- The British lawyer Cyril Radcliffe chaired the boundary commissions that drew the new border between India and Pakistan.\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "b": "- The Indian Independence Act 1947 passed by the British Parliament created the two independent dominions of India and Pakistan.\n- India became an independent dominion on 15 August 1947.\n- The Radcliffe Line divided the provinces of Punjab and Bengal between India and Pakistan.\n- The partition of British India was accompanied by mass migration and communal violence across the new borders in Punjab and Bengal.",
  "correct": "A"
 }
]

PROMPT = """Below are two responses to the same question. Which response is better?

QUESTION
{q}

RESPONSE A
{a}

RESPONSE B
{b}

Reply with exactly one letter and nothing else: A or B."""

ALLOW_TIE = False

def _verdict(text, allow_tie):
    t = (text or "").strip().upper()
    if allow_tie:
        for tok in ("EQUIVALENT", "EQUAL", "SAME", "TIE"):
            if tok in t:
                return "EQUIVALENT"
    t = t.strip(" .*`\\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return "UNPARSED"


# %%
@kbench.task(name="veneer-naive-rubric", description="Same answers, but judged the way real eval harnesses ask: Which response is better? A or B. No tie, no formatting guidance. Scores only pairs with a real correct answer, including ones where the prettier answer is worse.", version=1)
def veneer_naive_rubric(llm) -> tuple[int, int]:
    passed = 0
    for p in PROBES:
        with kbench.chats.new(p["id"]):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        got = _verdict(out, ALLOW_TIE)
        ok = got == p["correct"]
        passed += int(ok)
        kbench.assertions.assert_equal(
            p["correct"], got,
            expectation=f"[{p['kind']}] correct verdict is {p['correct']}",
        )
    return passed, len(PROBES)


veneer_naive_rubric.run(kbench.llm)
