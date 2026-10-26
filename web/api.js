async function runBattle(n){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),15000);
  try{
    const response=await fetch('/api/battle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({n}),signal:controller.signal});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||'No se pudo completar la carrera');
    return data;
  }finally{clearTimeout(timer)}
}
