const $=id=>document.getElementById(id);
const money=v=>new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(Number(v||0));
const num=v=>new Intl.NumberFormat("en-IN").format(Number(v||0));
const colors=["#8068ec","#38b88a","#f2a65a","#5593ed","#e879a9","#9babc4"];
let trendChart,categoryChart,regionChart,sales=[];
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function qs(obj){const p=new URLSearchParams();Object.entries(obj).forEach(([k,v])=>{if(v)p.set(k,v)});return p.toString()}
function currentFilters(){return {start:$("start").value,end:$("end").value}}
async function api(url,opts={}){const r=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});let d={};try{d=await r.json()}catch{}if(!r.ok)throw Error(d.error||"Request failed");return d}
function toast(msg){const t=$("toast");t.textContent=msg;t.classList.add("show");clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.classList.remove("show"),2600)}
function drawCharts(d){
 if(trendChart)trendChart.destroy();if(categoryChart)categoryChart.destroy();if(regionChart)regionChart.destroy();
 trendChart=new Chart($("trendChart"),{type:"line",data:{labels:d.monthly.map(x=>x.month),datasets:[{label:"Revenue",data:d.monthly.map(x=>x.revenue),borderColor:"#8068ec",backgroundColor:"#8068ec18",fill:true,tension:.38,borderWidth:2.5,pointRadius:3},{label:"Profit",data:d.monthly.map(x=>x.profit),borderColor:"#38b88a",tension:.38,borderWidth:2.5,pointRadius:3}]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${money(c.raw)}`}}},scales:{x:{grid:{display:false},ticks:{color:"#989daf",font:{size:10}}},y:{beginAtZero:true,grid:{color:"#f0f1f6"},ticks:{color:"#989daf",font:{size:9},callback:v=>v>=100000?`₹${(v/100000).toFixed(1)}L`:v>=1000?`₹${v/1000}k`:`₹${v}`}}}});
 categoryChart=new Chart($("categoryChart"),{type:"doughnut",data:{labels:d.categories.map(x=>x.category),datasets:[{data:d.categories.map(x=>x.revenue),backgroundColor:colors,borderWidth:3,borderColor:"#fff",hoverOffset:5}]},options:{responsive:true,maintainAspectRatio:false,cutout:"70%",plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.label}: ${money(c.raw)}`}}}});
 $("categoryLegend").innerHTML=d.categories.map((x,i)=>`<div><i style="background:${colors[i%colors.length]}"></i>${esc(x.category)}<b>${money(x.revenue)}</b></div>`).join("")||"No category data";
 regionChart=new Chart($("regionChart"),{type:"bar",data:{labels:d.regions.map(x=>x.region),datasets:[{data:d.regions.map(x=>x.revenue),backgroundColor:colors,borderRadius:5,maxBarThickness:36}]},options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>money(c.raw)}}},scales:{x:{beginAtZero:true,grid:{color:"#f0f1f6"},ticks:{color:"#989daf",font:{size:9},callback:v=>v>=1000?`₹${v/1000}k`:v}},y:{grid:{display:false},ticks:{color:"#686d7e",font:{size:10}}}}}});
 $("topProducts").innerHTML=d.top_products.map((x,i)=>`<div class="product-row"><div class="rank">${String(i+1).padStart(2,"0")}</div><div><div class="product-name">${esc(x.product)}</div><div class="product-sub">${num(x.units)} units sold</div></div><div class="product-revenue">${money(x.revenue)}</div></div>`).join("")||"No product data";
}
async function loadDashboard(){const d=await api("/api/dashboard?"+qs(currentFilters()));const s=d.summary;$("revenue").textContent=money(s.revenue);$("profit").textContent=money(s.profit);$("orders").textContent=num(s.orders);$("aov").textContent=money(s.average_order_value);$("margin").textContent=`${Number(s.profit_margin).toFixed(1)}% margin`;$("units").textContent=`${num(s.units)} units sold`;drawCharts(d)}
function fillFilterOptions(){
 const cat=$("categoryFilter").value,reg=$("regionFilter").value;
 const cats=["Accessories","Electronics","Furniture","Home & Office","Other"],regs=["Central","East","North","South","West"];
 $("categoryFilter").innerHTML='<option value="">All categories</option>'+cats.map(x=>`<option>${x}</option>`).join("");
 $("regionFilter").innerHTML='<option value="">All regions</option>'+regs.map(x=>`<option>${x}</option>`).join("");
 $("categoryFilter").value=cat;$("regionFilter").value=reg;
}
async function loadSales(){
 const d={...currentFilters(),search:$("search").value.trim(),category:$("categoryFilter").value,region:$("regionFilter").value};
 sales=await api("/api/sales?"+qs(d));fillFilterOptions();
 $("recordCount").textContent=`${sales.length} record${sales.length===1?"":"s"}`;
 if(!sales.length){$("salesTable").innerHTML='<tr><td colspan="10" class="empty">No sales found. Change your filters or add a sale.</td></tr>';return}
 $("salesTable").innerHTML=sales.map(s=>{const cls=s.category==="Accessories"?"accessories":s.category==="Furniture"?"furniture":s.category==="Home & Office"?"home-office":"";return `<tr><td class="order">#SL-${String(s.id).padStart(4,"0")}</td><td>${esc(s.order_date)}</td><td class="customer-cell">${esc(s.customer)}</td><td>${esc(s.product)}</td><td><span class="pill ${cls}">${esc(s.category)}</span></td><td>${esc(s.region)}</td><td>${num(s.quantity)}</td><td><b>${money(s.revenue)}</b></td><td class="profit-cell">${money(s.profit)}</td><td><div class="actions"><button class="icon-btn" data-edit="${s.id}" title="Edit">✎</button><button class="icon-btn" data-delete="${s.id}" title="Delete">⌫</button></div></td></tr>`}).join("");
}
async function refresh(){try{await Promise.all([loadDashboard(),loadSales()])}catch(e){toast(e.message);console.error(e)}}
function openModal(s=null){
 $("saleForm").reset();$("formError").textContent="";$("saleId").value=s?.id||"";$("modalTitle").textContent=s?"Edit sale":"Add new sale";$("saveBtn").textContent=s?"Save changes":"Save sale";
 $("orderDate").value=s?.order_date||new Date().toISOString().slice(0,10);
 if(s){$("customer").value=s.customer;$("product").value=s.product;$("category").value=s.category;$("region").value=s.region;$("payment").value=s.payment_method;$("quantity").value=s.quantity;$("price").value=s.unit_price;$("cost").value=s.unit_cost}else{$("quantity").value=1}
 $("modalBackdrop").classList.add("open");setTimeout(()=>$("customer").focus(),40)
}
function closeModal(){$("modalBackdrop").classList.remove("open")}
$("addTop").onclick=()=>openModal();$("addRecord").onclick=()=>openModal();$("closeModal").onclick=closeModal;$("cancelModal").onclick=closeModal;
$("modalBackdrop").onclick=e=>{if(e.target===$("modalBackdrop"))closeModal()};document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal()});
$("apply").onclick=refresh;$("reset").onclick=()=>{$("start").value="";$("end").value="";$("categoryFilter").value="";$("regionFilter").value="";$("search").value="";refresh()};
let timer;$("search").oninput=()=>{clearTimeout(timer);timer=setTimeout(loadSales,220)};$("categoryFilter").onchange=loadSales;$("regionFilter").onchange=loadSales;
$("menuBtn").onclick=()=>$("sidebar").classList.toggle("open");
$("salesTable").onclick=async e=>{const edit=e.target.closest("[data-edit]"),del=e.target.closest("[data-delete]");if(edit){const s=sales.find(x=>x.id===Number(edit.dataset.edit));if(s)openModal(s)}if(del){const id=Number(del.dataset.delete);if(!confirm("Delete this sales record?"))return;try{await api(`/api/sales/${id}`,{method:"DELETE"});toast("Sales record deleted.");await refresh()}catch(err){toast(err.message)}}};
$("saleForm").onsubmit=async e=>{e.preventDefault();$("formError").textContent="";const payload={order_date:$("orderDate").value,customer:$("customer").value.trim(),product:$("product").value.trim(),category:$("category").value,region:$("region").value,payment_method:$("payment").value,quantity:$("quantity").value,unit_price:$("price").value,unit_cost:$("cost").value};const id=$("saleId").value;$("saveBtn").disabled=true;try{await api(id?`/api/sales/${id}`:"/api/sales",{method:id?"PUT":"POST",body:JSON.stringify(payload)});closeModal();toast(id?"Sale updated successfully.":"Sale added successfully.");await refresh()}catch(err){$("formError").textContent=err.message}finally{$("saveBtn").disabled=false;$("saveBtn").textContent=id?"Save changes":"Save sale"}};
refresh();
