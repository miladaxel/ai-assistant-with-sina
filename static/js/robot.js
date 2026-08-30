
let flow=document.createElement("a")
flow.href=SITE_URLS.robot

flow.style=`  position: fixed;
    background-color: var(--primary);
    padding: 1rem;
    z-index: 9999;
    border-radius: 300px;
    bottom: 2rem;
    left: 2rem;
    display: flex;
    width: 80px;
    height: 80px;
    align-items: center;
    justify-content: center;`
flow.innerHTML=`
    
        <img style="width:50px" src="${SIDEBAR_ICONS.robot}" />
    
`
document.body.prepend(flow);