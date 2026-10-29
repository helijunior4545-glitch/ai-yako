
(function () {
  'use strict';
  const demos = [
    ['Detect Investment Fraud', 'An investment platform promises a guaranteed 30% monthly return, requires an immediate deposit, and provides no independent audit. Identify the warning signs and explain what evidence is missing.'],
    ['Analyze Financial Risk', 'I have $10,000. One investment offers a guaranteed 25% monthly return, while another offers an estimated 6% annual return with market risk. Compare the claims, uncertainty, and potential warning signs.'],
    ['Evaluate Cash Flow', 'My monthly income is $5,200. Rent is $1,600, food is $650, transport is $350, utilities are $300, and debt payments are $900. Calculate my remaining cash flow and identify financial vulnerabilities.'],
    ['Compare Investment Scenarios', 'Compare investing $5,000 for one year at 4%, 7%, and 10% annual returns, assuming annual compounding, no additional deposits, and no fees or taxes. Calculate the ending value for each scenario.'],
    ['Build a Financial Strategy', 'My monthly income is $4,000, essential expenses are $2,500, and debt payments are $600. I have $1,000 in savings. Propose a realistic six-month emergency-fund strategy using only the available monthly surplus.']
  ];
  function install() {
    const existing = document.querySelector('.suggestions [data-prompt]');
    if (!existing || !existing.parentElement) return;
    const parent = existing.parentElement;
    const originals = Array.from(parent.querySelectorAll('[data-prompt]'));
    originals.forEach(b => { b.hidden = true; b.style.display = 'none'; });
    if (document.querySelector('[data-yako-v1060-demo]')) return;
    demos.forEach(([label, prompt]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = existing.className;
      button.textContent = label;
      button.setAttribute('data-yako-v1060-demo', '1');
      button.addEventListener('click', () => {
        const oldPrompt = existing.dataset.prompt;
        existing.dataset.prompt = prompt;
        existing.click();
        existing.dataset.prompt = oldPrompt;
      });
      parent.appendChild(button);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();
