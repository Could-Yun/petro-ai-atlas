const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..'),ctx={};ctx.window=ctx;vm.createContext(ctx);
for(const f of ['science.js','flow-sketches.js','figures.js'])vm.runInContext(fs.readFileSync(path.join(root,'assets',f),'utf8'),ctx);
const catalog=JSON.parse(fs.readFileSync(path.join(root,'assets/catalog.js'),'utf8').replace(/^window.CATALOG=/,'').replace(/;$/,'')),out={},flows={};
for(const c of catalog){out[c.id]=[0,1,2].map(k=>ctx.PetroFigures.render(c,k));flows[c.id]=c.steps.map((_,i)=>ctx.PetroFigures.workflow(c,i))}
fs.writeFileSync(path.join(root,'assets/theories.json'),JSON.stringify(out));fs.writeFileSync(path.join(root,'assets/workflows.json'),JSON.stringify(flows));console.log('Generated 27 concept states and 36 distinct workflow diagrams from shared contracts.');
