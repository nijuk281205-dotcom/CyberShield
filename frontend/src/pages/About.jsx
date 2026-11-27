export default function About() {
  return (
    <>
      <header className="page-head">
        <h1>How CyberShield decides</h1>
        <p>A transparent set of rules, not a black box.</p>
      </header>
      <section className="card prose">
        <h2>What we look at in a link</h2>
        <ul>
          <li>An IP address where a domain name should be</li>
          <li>Missing HTTPS, very long links, many subdomains or hyphens</li>
          <li>Look-alike (punycode) characters and brand names in the wrong place</li>
          <li>Risky domain endings, URL shorteners, '@' tricks, unusual ports</li>
          <li>Words such as login, verify, prize or refund</li>
        </ul>
        <h2>What we look at in a message</h2>
        <ul>
          <li>Urgency and threats, requests for OTP, PIN or passwords</li>
          <li>Prize offers, money transfer requests, KYC or account warnings</li>
          <li>Risky links and unknown phone numbers</li>
        </ul>
        <h2>How the score maps to a level</h2>
        <p>Each indicator adds points. 0 to 24 is Low, 25 to 54 is Medium, 55 and above is High.</p>
        <h2>Limits you should know</h2>
        <p>CyberShield never opens the link and does not query threat databases. New or well-crafted scams can score Low, and
          some honest sites can score higher than expected. Treat results as guidance. When money or passwords are involved,
          confirm through the organisation's official website or app.</p>
        <p>Reporting a scam in India: cybercrime.gov.in or helpline 1930.</p>
      </section>
    </>
  );
}
