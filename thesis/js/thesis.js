(function(){
  const data=window.THESIS_DATA||{summary:{nominal:[],nominal_improvements_vs_cmos:[]}};
  const fmt=(v,s=1,d=3)=>typeof v==='number'?(v*s).toFixed(d):'—';
  function table(rows, columns, caption){
    const head=columns.map(c=>`<th>${c[0]}</th>`).join('');
    const body=rows.map(r=>`<tr>${columns.map(c=>`<td>${c[1](r)}</td>`).join('')}</tr>`).join('');
    return `<table><caption>${caption}</caption><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
  }
  const nominal=data.summary.nominal||[];
  const encoderCols=[['Architecture',r=>r.architecture],['Power (uW)',r=>fmt(r.pavg,1e6)],['Delay (ps)',r=>fmt(r.tpd,1e12)],['PDP (fJ)',r=>fmt(r.pdp,1e15)],['Swing (V)',r=>fmt(r.output_swing)],['Transistors',r=>r.transistor_count],['Functional',r=>r.functional_pass?'Pass':'Fail']];
  document.getElementById('h117-table').innerHTML=table(nominal.filter(r=>r.level==='H117'),encoderCols,'Table 4.1. Reproduced nominal Hamming (11,7) results.');
  document.getElementById('eh127-table').innerHTML=table(nominal.filter(r=>r.level==='EH127'),encoderCols,'Table 8.1. Nominal extended Hamming (12,7) LTspice results.');
  const improvements=(data.summary.nominal_improvements_vs_cmos||[]).filter(r=>r.level==='EH127');
  document.getElementById('improvement-table').innerHTML=table(improvements,[['Architecture',r=>r.architecture],['Power improvement (%)',r=>fmt(r.power_improvement_pct)],['Delay improvement (%)',r=>fmt(r.delay_improvement_pct)],['PDP improvement (%)',r=>fmt(r.pdp_improvement_pct)],['Transistor reduction (%)',r=>fmt(r.transistor_reduction_pct)]],'Table 9.1. Nominal change relative to CMOS; negative values indicate degradation.');
})();

