const API_BASE="https://YOUR-API.onrender.com";
const topics=document.querySelector("#topics"), result=document.querySelector("#result"), cohort=document.querySelector("#cohort");
async function loadTopics(){const r=await fetch(`${API_BASE}/api/topics?class_level=${cohort.value}`);const d=await r.json();topics.innerHTML=d.map(x=>`<label class="bg-slate-800 p-3 rounded"><input type="checkbox" value="${x.id}"> ${x.subject} — ${x.name}</label>`).join("");}
async function generate(){const ids=[...topics.querySelectorAll("input:checked")].map(x=>+x.value);if(!ids.length)return alert("Select a topic");const r=await fetch(`${API_BASE}/api/generate-test`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cohort:cohort.value,topic_ids:ids,difficulty:"Medium",count:10})});result.textContent=JSON.stringify(await r.json(),null,2);}
document.querySelector("#load").onclick=loadTopics;document.querySelector("#generate").onclick=generate;loadTopics().catch(()=>{});
