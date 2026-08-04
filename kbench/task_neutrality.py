# %%
"""VENEER — format neutrality. How far does presentation alone tilt a judge?

Every pair below is ONE list of atomic factual claims rendered two ways. The
content is byte-identical at the claim level; only presentation differs. Each
pair is shown in BOTH orders, and the judge is asked the way real eval harnesses
ask: "Which response is better? A or B." No tie option, no formatting guidance.

Because the content is identical there is no per-probe right answer. What is
measurable is the systematic tilt:

    format_index = mean over renderings of |formatted_twice - plain_twice| / n
    score        = 100 * (1 - format_index)      higher = more format-neutral

The mean is over renderings and uses absolute values, so a judge that prefers
bullets and dislikes padding cannot cancel those into a fake 100 -- pooling
would have done exactly that.

A judge that always picks the same POSITION scores as neutral here by design: it
is not being swayed by formatting. Its position rate is printed separately.

Corpus, harness and methodology:
https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias
"""

# %%
import kaggle_benchmarks as kbench
import collections

# %%
PROBES = [
 {
  "pair": "science-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below **atmospheric** pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by **capillaries**. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy **expenditure** by the lungs. About **98 percent** of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of **capillary** blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives **breathing** rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/table",
  "fmt": "table",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. |\n| 2 | Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. |\n| 3 | Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. |\n| 4 | About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. |\n| 5 | Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. |\n| 6 | The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. |",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely **proportional** to the fourth power of the wavelength of the light.\n- Blue light near **450 nanometres** is scattered by air molecules several times more strongly than red light near **700 nanometres**.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the **Sun**.\n- Sunlight passes through a far longer path of atmosphere when the **Sun** is near the horizon than when the **Sun** is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long **atmospheric** path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of **Earth**'s atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/table",
  "fmt": "table",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. |\n| 2 | Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. |\n| 3 | Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. |\n| 4 | About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. |\n| 5 | Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. |\n| 6 | The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. |",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on **28 June** **1919 at** the Palace of Versailles in France. The Treaty of **Versailles** ended the state of war between **Germany** and the Allied powers of World War I. Article **231 of** the **Treaty** of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of **Versailles** obliged **Germany** to pay reparations to the Allied powers. The Treaty of **Versailles** restricted the German army to a maximum of **100,000 men**. The Treaty of **Versailles** transferred the territory of **Alsace**-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "1. HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n2. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n3. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n4. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n5. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n6. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/table",
  "fmt": "table",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. |\n| 2 | Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. |\n| 3 | The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. |\n| 4 | Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. |\n| 5 | Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. |\n| 6 | Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. |",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "🔹 The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n✅ The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n📌 Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n💡 The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n🔎 The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n⚡ The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "1. Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n2. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n3. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n4. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n5. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n6. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that the Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. This is a well-established point. To put it simply, the Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. That detail matters here. In practical terms, article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. This is generally the case. As a general rule, the Treaty of Versailles obliged Germany to pay reparations to the Allied powers. That is the usual situation. Broadly speaking, the Treaty of Versailles restricted the German army to a maximum of 100,000 men. This holds in most circumstances. Put another way, the Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Treaty of Versailles was signed on **28 June** **1919 at** the Palace of Versailles in France.\n- The Treaty of **Versailles** ended the state of war between **Germany** and the Allied powers of World War I.\n\n## Key Details\n- Article **231 of** the **Treaty** of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of **Versailles** obliged **Germany** to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of **Versailles** restricted the German army to a maximum of **100,000 men**.\n- The Treaty of **Versailles** transferred the territory of **Alsace**-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "🔹 The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n✅ Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n📌 Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n💡 About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n🔎 Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n⚡ The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that the diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. This is a well-established point. To put it simply, inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. That detail matters here. In practical terms, oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. This is generally the case. As a general rule, about 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. That is the usual situation. Broadly speaking, carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. This holds in most circumstances. Put another way, the main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "🔹 The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n✅ Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n📌 Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n💡 About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n🔎 Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n⚡ The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "1. The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n2. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n3. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n4. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n5. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n6. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/table",
  "fmt": "table",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. |\n| 2 | The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. |\n| 3 | Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. |\n| 4 | The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. |\n| 5 | The Treaty of Versailles restricted the German army to a maximum of 100,000 men. |\n| 6 | The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. |",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/table",
  "fmt": "table",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. |\n| 2 | The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. |\n| 3 | The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. |\n| 4 | Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. |\n| 5 | Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. |\n| 6 | Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. |",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. This is a well-established point. To put it simply, blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. That detail matters here. In practical terms, the daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. This is generally the case. As a general rule, sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. That is the usual situation. Broadly speaking, sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. This holds in most circumstances. Put another way, sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. This is a well-established point. To put it simply, blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. That detail matters here. In practical terms, the daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. This is generally the case. As a general rule, sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. That is the usual situation. Broadly speaking, sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. This holds in most circumstances. Put another way, sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "## Overview\n- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely **proportional** to the fourth power of the wavelength of the light. Blue light near **450 nanometres** is scattered by air molecules several times more strongly than red light near **700 nanometres**. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the **Sun**. Sunlight passes through a far longer path of atmosphere when the **Sun** is near the horizon than when the **Sun** is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long **atmospheric** path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of **Earth**'s atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The Treaty of Versailles was signed on **28 June** **1919 at** the Palace of Versailles in France.\n- The Treaty of **Versailles** ended the state of war between **Germany** and the Allied powers of World War I.\n\n## Key Details\n- Article **231 of** the **Treaty** of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of **Versailles** obliged **Germany** to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of **Versailles** restricted the German army to a maximum of **100,000 men**.\n- The Treaty of **Versailles** transferred the territory of **Alsace**-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "1. HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n2. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n3. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n4. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n5. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n6. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The federal funds rate is the interest rate at which depository **institutions** lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight **scheduled** meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the **effective** federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, **adjustable**-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing **construction**, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that **economists** commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/table",
  "fmt": "table",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. |\n| 2 | Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. |\n| 3 | The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. |\n| 4 | Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. |\n| 5 | Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. |\n| 6 | Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet. |",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. This is a well-established point. To put it simply, a lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. That detail matters here. In practical terms, the red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. This is generally the case. As a general rule, the last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. That is the usual situation. Broadly speaking, a battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. This holds in most circumstances. Put another way, driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port **443 by** default.\n- TLS uses asymmetric public key **cryptography** during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric **encryption** is far faster than asymmetric encryption.\n- A TLS **certificate** binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-**Hellman** key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses **authenticated** encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "## Overview\n- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "🔹 The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n✅ The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n📌 The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n💡 Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n🔎 Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n⚡ Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/table",
  "fmt": "table",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. |\n| 2 | A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. |\n| 3 | The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. |\n| 4 | The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. |\n| 5 | A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. |\n| 6 | Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. |",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Both vehicles must use the same electrical system voltage, which is **12 volts** for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a **misplaced** cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the **positive** terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an **unpainted** metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A **battery** that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for **20 to** **30 minutes** lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "🔹 Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n✅ Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n📌 The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n💡 Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n🔎 Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n⚡ Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below **atmospheric** pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by **capillaries**. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy **expenditure** by the lungs. About **98 percent** of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of **capillary** blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives **breathing** rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "🔹 Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n✅ A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n📌 The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n💡 The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n🔎 A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n⚡ Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port **443 by** default. TLS uses asymmetric public key **cryptography** during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric **encryption** is far faster than asymmetric encryption. A TLS **certificate** binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-**Hellman** key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses **authenticated** encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that hTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. This is a well-established point. To put it simply, tLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. That detail matters here. In practical terms, application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. This is generally the case. As a general rule, a TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. That is the usual situation. Broadly speaking, ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. This holds in most circumstances. Put another way, tLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is **12 volts** for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a **misplaced** cable clamp. The red clamps of a jumper cable set attach to the **positive** terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an **unpainted** metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A **battery** that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for **20 to** **30 minutes** lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository **institutions** lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight **scheduled** meetings each year. The Federal Reserve keeps the **effective** federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, **adjustable**-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing **construction**, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that **economists** commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that hTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. This is a well-established point. To put it simply, tLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. That detail matters here. In practical terms, application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. This is generally the case. As a general rule, a TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. That is the usual situation. Broadly speaking, ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. This holds in most circumstances. Put another way, tLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository **institutions** lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight **scheduled** meetings each year. The Federal Reserve keeps the **effective** federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, **adjustable**-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing **construction**, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that **economists** commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/table",
  "fmt": "table",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. |\n| 2 | A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. |\n| 3 | The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. |\n| 4 | The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. |\n| 5 | A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. |\n| 6 | Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. |",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely **proportional** to the fourth power of the wavelength of the light. Blue light near **450 nanometres** is scattered by air molecules several times more strongly than red light near **700 nanometres**. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the **Sun**. Sunlight passes through a far longer path of atmosphere when the **Sun** is near the horizon than when the **Sun** is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long **atmospheric** path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of **Earth**'s atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "## Overview\n- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n\n## Key Details\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/table",
  "fmt": "table",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. |\n| 2 | The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. |\n| 3 | Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. |\n| 4 | The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. |\n| 5 | The Treaty of Versailles restricted the German army to a maximum of 100,000 men. |\n| 6 | The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. |",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "1. The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n2. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n3. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n4. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n5. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n6. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "1. The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n2. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n3. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n4. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n5. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n6. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "1. Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n2. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n3. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n4. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n5. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n6. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs.\n- About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "🔹 Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n✅ Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n📌 The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n💡 Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n🔎 Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n⚡ Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that the Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. This is a well-established point. To put it simply, the Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. That detail matters here. In practical terms, article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. This is generally the case. As a general rule, the Treaty of Versailles obliged Germany to pay reparations to the Allied powers. That is the usual situation. Broadly speaking, the Treaty of Versailles restricted the German army to a maximum of 100,000 men. This holds in most circumstances. Put another way, the Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/bullets",
  "fmt": "bullets",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "🔹 The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n✅ The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n📌 The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n💡 Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n🔎 Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n⚡ Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. This is a well-established point. To put it simply, a lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. That detail matters here. In practical terms, the red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. This is generally the case. As a general rule, the last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. That is the usual situation. Broadly speaking, a battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. This holds in most circumstances. Put another way, driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that the diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. This is a well-established point. To put it simply, inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. That detail matters here. In practical terms, oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. This is generally the case. As a general rule, about 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. That is the usual situation. Broadly speaking, carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. This holds in most circumstances. Put another way, the main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "🔹 HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n✅ TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n📌 Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n💡 A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n🔎 Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n⚡ TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "health-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below **atmospheric** pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by **capillaries**.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy **expenditure** by the lungs.\n- About **98 percent** of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of **capillary** blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives **breathing** rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely **proportional** to the fourth power of the wavelength of the light.\n- Blue light near **450 nanometres** is scattered by air molecules several times more strongly than red light near **700 nanometres**.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the **Sun**.\n- Sunlight passes through a far longer path of atmosphere when the **Sun** is near the horizon than when the **Sun** is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long **atmospheric** path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of **Earth**'s atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is **12 volts** for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a **misplaced** cable clamp. The red clamps of a jumper cable set attach to the **positive** terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an **unpainted** metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A **battery** that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for **20 to** **30 minutes** lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "health-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "How does oxygen get from the air I breathe into my bloodstream?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below **atmospheric** pressure so air flows in.\n- Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by **capillaries**.\n\n## Key Details\n- Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy **expenditure** by the lungs.\n- About **98 percent** of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma.\n\n## Additional Context\n- Carbon dioxide diffuses out of **capillary** blood into the alveoli and leaves the body in exhaled air.\n- The main stimulus that drives **breathing** rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "b": "The diaphragm contracts and flattens during inhalation, which enlarges the chest cavity and drops the pressure inside the lungs below atmospheric pressure so air flows in. Inhaled air travels down the trachea and branching bronchi into hundreds of millions of alveoli, which are thin-walled air sacs surrounded by capillaries. Oxygen crosses the alveolar wall into capillary blood by passive diffusion down a partial pressure gradient, requiring no energy expenditure by the lungs. About 98 percent of the oxygen carried in blood is bound to hemoglobin inside red blood cells rather than dissolved in the plasma. Carbon dioxide diffuses out of capillary blood into the alveoli and leaves the body in exhaled air. The main stimulus that drives breathing rate in a healthy person is rising carbon dioxide in the blood rather than falling oxygen.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "1. The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n2. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n3. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n4. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n5. The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n6. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "1. The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n2. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n3. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n4. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n5. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n6. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/padded",
  "fmt": "padded",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "Here is a summary of the main points relevant to this question. It is worth noting that the federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. This is a well-established point. To put it simply, the Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. That detail matters here. In practical terms, the Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. This is generally the case. As a general rule, changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. That is the usual situation. Broadly speaking, higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. This holds in most circumstances. Put another way, monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- The federal funds rate is the interest rate at which depository **institutions** lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight **scheduled** meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the **effective** federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, **adjustable**-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing **construction**, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that **economists** commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/markdown_max",
  "fmt": "markdown_max",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- Both vehicles must use the same electrical system voltage, which is **12 volts** for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a **misplaced** cable clamp.\n\n## Key Details\n- The red clamps of a jumper cable set attach to the **positive** terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an **unpainted** metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n\n## Additional Context\n- A **battery** that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for **20 to** **30 minutes** lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "## Overview\n- The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n- The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n\n## Key Details\n- Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n- The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n\n## Additional Context\n- The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n- The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "science-00/numbered",
  "fmt": "numbered",
  "order": 1,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "1. Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n2. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n3. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n4. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n5. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n6. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "A"
 },
 {
  "pair": "history-00/bold_terms",
  "fmt": "bold_terms",
  "order": 1,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on **28 June** **1919 at** the Palace of Versailles in France. The Treaty of **Versailles** ended the state of war between **Germany** and the Allied powers of World War I. Article **231 of** the **Treaty** of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of **Versailles** obliged **Germany** to pay reparations to the Allied powers. The Treaty of **Versailles** restricted the German army to a maximum of **100,000 men**. The Treaty of **Versailles** transferred the territory of **Alsace**-Lorraine from Germany to France.",
  "b": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/table",
  "fmt": "table",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "| Point | Detail |\n| --- | --- |\n| 1 | HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. |\n| 2 | TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. |\n| 3 | Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. |\n| 4 | A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. |\n| 5 | Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. |\n| 6 | TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. |",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n- TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n- A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/table",
  "fmt": "table",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. |\n| 2 | The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. |\n| 3 | The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. |\n| 4 | Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. |\n| 5 | Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. |\n| 6 | Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. |",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "## Overview\n- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/markdown_max",
  "fmt": "markdown_max",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "**Here is a summary of the main points relevant to this question.**\n\n## Overview\n- HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port **443 by** default.\n- TLS uses asymmetric public key **cryptography** during its handshake to authenticate the server and agree on shared secret keys.\n\n## Key Details\n- Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric **encryption** is far faster than asymmetric encryption.\n- A TLS **certificate** binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n\n## Additional Context\n- Ephemeral Diffie-**Hellman** key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n- TLS uses **authenticated** encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/bold_terms",
  "fmt": "bold_terms",
  "order": 0,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port **443 by** default. TLS uses asymmetric public key **cryptography** during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric **encryption** is far faster than asymmetric encryption. A TLS **certificate** binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-**Hellman** key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses **authenticated** encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "B"
 },
 {
  "pair": "everyday-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "🔹 Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n✅ A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n📌 The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n💡 The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n🔎 A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n⚡ Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "science-00/headers",
  "fmt": "headers",
  "order": 0,
  "q": "Why is the sky blue during the day but red or orange at sunrise and sunset?",
  "a": "Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light. Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres. The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun. Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead. Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths. Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "b": "## Overview\n- Rayleigh scattering of sunlight by air molecules has an intensity that is inversely proportional to the fourth power of the wavelength of the light.\n- Blue light near 450 nanometres is scattered by air molecules several times more strongly than red light near 700 nanometres.\n\n## Key Details\n- The daytime sky looks blue because scattered short wavelength sunlight arrives at an observer from every direction across the sky rather than only from the direction of the Sun.\n- Sunlight passes through a far longer path of atmosphere when the Sun is near the horizon than when the Sun is high overhead.\n\n## Additional Context\n- Sunlight seen at sunrise or sunset has lost much of its blue component to scattering along the long atmospheric path, leaving the transmitted beam dominated by red and orange wavelengths.\n- Sunlight reaching the top of Earth's atmosphere contains less violet light than blue light, which contributes to the sky appearing blue rather than violet.",
  "formatted_is": "B"
 },
 {
  "pair": "tech-00/emoji",
  "fmt": "emoji",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "🔹 HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default.\n✅ TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys.\n📌 Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption.\n💡 A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts.\n🔎 Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions.\n⚡ TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "- Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n- A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n- The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n- The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n- A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n- Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "A"
 },
 {
  "pair": "economics-00/headers",
  "fmt": "headers",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "## Overview\n- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n\n## Key Details\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n\n## Additional Context\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
 },
 {
  "pair": "tech-00/table",
  "fmt": "table",
  "order": 1,
  "q": "How does HTTPS keep data secure between a browser and a web server?",
  "a": "| Point | Detail |\n| --- | --- |\n| 1 | HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. |\n| 2 | TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. |\n| 3 | Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. |\n| 4 | A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. |\n| 5 | Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. |\n| 6 | TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver. |",
  "b": "HTTPS carries ordinary HTTP messages over a TLS-encrypted connection, which uses TCP port 443 by default. TLS uses asymmetric public key cryptography during its handshake to authenticate the server and agree on shared secret keys. Application data in TLS is protected with symmetric ciphers such as AES-GCM or ChaCha20-Poly1305 because symmetric encryption is far faster than asymmetric encryption. A TLS certificate binds a domain name to a public key and carries a signature from a certificate authority that the client already trusts. Ephemeral Diffie-Hellman key exchange gives forward secrecy, so stealing a server's long-term private key later does not decrypt previously recorded sessions. TLS uses authenticated encryption, so a record modified by an attacker in transit fails its integrity check and is rejected by the receiver.",
  "formatted_is": "A"
 },
 {
  "pair": "everyday-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "How do I safely jump-start a car with a dead battery using jumper cables?",
  "a": "Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "b": "1. Both vehicles must use the same electrical system voltage, which is 12 volts for nearly all modern passenger cars.\n2. A lead-acid car battery vents hydrogen gas, which can be ignited by a spark from a misplaced cable clamp.\n3. The red clamps of a jumper cable set attach to the positive terminal of the dead battery and the positive terminal of the donor battery.\n4. The last clamp should be attached to an unpainted metal surface on the engine block or frame of the disabled car rather than to its negative battery terminal.\n5. A battery that is frozen, visibly cracked, or leaking must not be jump-started because it can rupture.\n6. Driving the revived vehicle for 20 to 30 minutes lets the alternator restore meaningful charge to the battery.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/numbered",
  "fmt": "numbered",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "1. The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n2. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n3. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n4. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n5. The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n6. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/padded",
  "fmt": "padded",
  "order": 0,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "Here is a summary of the main points relevant to this question. It is worth noting that the federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. This is a well-established point. To put it simply, the Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. That detail matters here. In practical terms, the Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. This is generally the case. As a general rule, changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. That is the usual situation. Broadly speaking, higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. This holds in most circumstances. Put another way, monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years. That is worth keeping in mind. Taken together, these points cover the essentials of the question.",
  "formatted_is": "B"
 },
 {
  "pair": "history-00/emoji",
  "fmt": "emoji",
  "order": 0,
  "q": "What did the Treaty of Versailles do at the end of World War I?",
  "a": "The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France. The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I. Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I. The Treaty of Versailles obliged Germany to pay reparations to the Allied powers. The Treaty of Versailles restricted the German army to a maximum of 100,000 men. The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "b": "🔹 The Treaty of Versailles was signed on 28 June 1919 at the Palace of Versailles in France.\n✅ The Treaty of Versailles ended the state of war between Germany and the Allied powers of World War I.\n📌 Article 231 of the Treaty of Versailles assigned Germany responsibility for the loss and damage caused by World War I.\n💡 The Treaty of Versailles obliged Germany to pay reparations to the Allied powers.\n🔎 The Treaty of Versailles restricted the German army to a maximum of 100,000 men.\n⚡ The Treaty of Versailles transferred the territory of Alsace-Lorraine from Germany to France.",
  "formatted_is": "B"
 },
 {
  "pair": "economics-00/bullets",
  "fmt": "bullets",
  "order": 1,
  "q": "How does the Federal Reserve's federal funds rate influence the broader economy?",
  "a": "- The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight.\n- The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year.\n- The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks.\n- Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt.\n- Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand.\n- Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "b": "The federal funds rate is the interest rate at which depository institutions lend reserve balances to one another overnight. The Federal Open Market Committee sets a target range for the federal funds rate at eight scheduled meetings each year. The Federal Reserve keeps the effective federal funds rate inside its target range primarily by adjusting the interest rate it pays on reserve balances held by banks. Changes in the federal funds rate pass through to other borrowing costs including bank prime rates, adjustable-rate mortgages, and short-term corporate debt. Higher policy rates tend to reduce interest-sensitive spending such as business investment and housing construction, which cools aggregate demand. Monetary policy affects output and inflation with long and variable lags that economists commonly estimate at roughly one to two years.",
  "formatted_is": "A"
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


def _letter(text):
    t = (text or "").strip().upper().strip(" .*`\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return None


# %%
@kbench.task(name="veneer-format-neutrality", description="Identical claims rendered two ways, every pair shown in both orders, forced A/B. Scores how far a judge's preference tilts on presentation alone: 100 = format-neutral, 0 = fully format-driven. Averaged per format so opposite biases cannot cancel out.", version=1)
def veneer_format_neutrality(llm) -> float:
    picked = {}
    for p in PROBES:
        with kbench.chats.new(f"{p['pair']}#{p['order']}"):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        L = _letter(out)
        if L is None:
            continue
        picked.setdefault(p["pair"], {})[p["order"]] = {
            "chose_formatted": L == p["formatted_is"], "letter": L, "fmt": p["fmt"]}

    per_fmt = collections.defaultdict(lambda: {"f": 0, "p": 0, "n": 0})
    same_position = total_pairs = 0
    for pair, seen in picked.items():
        if len(seen) < 2:
            continue
        o0, o1 = seen[0], seen[1]
        fmt = o0["fmt"]
        per_fmt[fmt]["n"] += 1
        total_pairs += 1
        if o0["chose_formatted"] and o1["chose_formatted"]:
            per_fmt[fmt]["f"] += 1
        elif not o0["chose_formatted"] and not o1["chose_formatted"]:
            per_fmt[fmt]["p"] += 1
        if o0["letter"] == o1["letter"]:
            same_position += 1

    tilts = []
    print("\n===== VENEER format neutrality =====")
    for fmt in sorted(per_fmt):
        d = per_fmt[fmt]
        tilt = abs(d["f"] - d["p"]) / d["n"]
        tilts.append(tilt)
        lean = "formatted" if d["f"] > d["p"] else ("plain" if d["p"] > d["f"] else "none")
        print(f"  {fmt:14s} formatted x2={d['f']:2d}  plain x2={d['p']:2d}  "
              f"n={d['n']:2d}  tilt={tilt:.2f} toward {lean}")
        kbench.assertions.assert_true(
            tilt <= 0.5,
            expectation=f"[{fmt}] presentation tilts the verdict by <=50% of pairs",
        )

    format_index = sum(tilts) / len(tilts) if tilts else 0.0
    score = round(100.0 * (1.0 - format_index), 2)
    pos_rate = same_position / total_pairs if total_pairs else 0.0
    print(f"  format_index = {format_index:.3f}   ->   NEUTRALITY SCORE = {score}")
    print(f"  position rate (same letter both orders) = {pos_rate:.2f} "
          f"[diagnostic, not scored]")
    return score


veneer_format_neutrality.run(kbench.llm)
