window.__ready=false;
import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs').then(async m=>{
  m.default.initialize({startOnLoad:false,state:{useMaxWidth:false},theme:'base',fontFamily:'PingFang SC, Microsoft YaHei, sans-serif',
    themeVariables:{primaryColor:'#e6f2ec',primaryBorderColor:'#2f7d62',primaryTextColor:'#1f2328',lineColor:'#5b6470',secondaryColor:'#e8eff8',tertiaryColor:'#fbf1e1',fontSize:'15px',actorBkg:'#e6f2ec',actorBorder:'#2f7d62',noteBkgColor:'#fbf1e1',noteBorderColor:'#b7791f'},
    flowchart:{useMaxWidth:false,curve:'basis',padding:14,nodeSpacing:40,rankSpacing:46},er:{useMaxWidth:false},sequence:{useMaxWidth:false,mirrorActors:false,messageMargin:28}});
  await m.default.run({querySelector:'.mermaid'}); window.__ready=true;});
