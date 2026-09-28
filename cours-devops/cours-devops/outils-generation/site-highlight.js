(function(){
/* Coloration syntaxique légère pour tout le site (bash, yaml, java, kotlin, js/ts, python, sql, hcl, html, dockerfile). Injectée par restyle.py. */
var KW = new RegExp('^(?:' + [
 'abstract','actual','as','async','await','break','case','catch','class','companion','const','constructor','continue','data','def','default','do','else','elif','enum','except','export','extends','final','finally','for','from','fun','function','if','implements','import','in','inline','interface','internal','is','lambda','lateinit','let','match','new','not','object','open','operator','override','package','pass','private','protected','public','raise','record','reified','return','sealed','static','suspend','switch','this','throw','throws','try','typealias','val','var','void','when','where','while','with','yield','and','or','null','true','false','None','True','False','undefined','nil',
 'resource','provider','variable','output','locals','module','terraform','data',
 'select','from','where','join','left','inner','outer','group','by','order','having','limit','offset','insert','into','values','update','set','delete','create','table','index','alter','add','drop','primary','key','references','on','using','exists','between','like','asc','desc','distinct','union','begin','commit','rollback','declare','partition','concurrently','not','null','default',
 'FROM','RUN','COPY','ADD','CMD','ENTRYPOINT','ENV','ARG','EXPOSE','USER','WORKDIR','VOLUME','HEALTHCHECK','LABEL','SHELL','AS',
 'docker','kubectl','helm','terraform','ansible-playbook','git','curl','wget','npm','npx','mvn','gradle','java','python3','python','pip','aws','az','gcloud','openssl','keytool','cosign','trivy','k6','psql','sudo','echo','cat','grep','sed','awk','ls','cd','mkdir','rm','cp','mv','chmod','chown','source','alias','done','then','fi','esac','exit','tar','zip','unzip','ssh','scp','systemctl','journalctl','vault','argocd','kind','jq','yq'
].join('|') + ')$');
var esc = function(t){ return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
var TOKEN = new RegExp([
 '(<!--[\\s\\S]*?-->|/\\*[\\s\\S]*?\\*/)',                                   // 1 commentaire bloc
 '((?<![:\\w/])//(?!/)[^\\n]*|#(?![0-9a-fA-F]{3,6}\\b)[^\\n]*|--\\s[^\\n]*)',            // 2 commentaire ligne
 '("""[\\s\\S]*?"""|\'\'\'[\\s\\S]*?\'\'\'|"(?:\\\\.|[^"\\\\\\n])*"|\'(?:\\\\.|[^\'\\\\\\n])*\'|`(?:\\\\.|[^`\\\\])*`)', // 3 chaîne
 '(^[ \\t]*(?:\\$|>>>|❯)(?=\\s))',                                          // 4 prompt
 '(^[ \\t]*[\\w.\\-/\\[\\]"\']+(?=:(?:\\s|$)))',                            // 5 clé yaml / json
 '(@[A-Za-z_][\\w.]*)',                                                      // 6 annotation
 '(\\$\\{?[A-Za-z_][\\w.]*\\}?|\\$\\d)',                                     // 7 variable shell
 '(</?[A-Za-z][\\w:.-]*(?=[\\s>/])|/?>(?=\\s|$|<))',                          // 8 balise
 '(\\b0x[0-9a-fA-F]+\\b|\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?[a-zA-Z%]{0,3}\\b)', // 9 nombre
 '(\\b[A-Za-z_][\\w.-]*\\b)',                                                // 10 mot
 '(=>|->|::|===|!==|==|!=|<=|>=|&&|\\|\\||\\?:|\\?\\.|!!|[+\\-*/%=<>!?&|^~])'  // 11 opérateur
].join('|'), 'gm');
function highlight(src){
 var out = '', last = 0, m;
 TOKEN.lastIndex = 0;
 while ((m = TOKEN.exec(src))) {
  out += esc(src.slice(last, m.index)); last = m.index + m[0].length;
  var t = m[0], cls = null;
  if (m[1] || m[2]) cls = 'com';
  else if (m[3]) cls = 'str';
  else if (m[4]) cls = 'prompt';
  else if (m[5]) cls = 'key';
  else if (m[6]) cls = 'ann';
  else if (m[7]) cls = 'var';
  else if (m[8]) cls = 'tag';
  else if (m[9]) cls = 'num';
  else if (m[10]) { if (KW.test(t)) cls = 'kw'; else if (/^[A-Z][A-Za-z0-9_]*$/.test(t)) cls = 'type'; else if (/\(/.test(src.slice(last, last + 2)) || src.charAt(last) === '(') cls = 'fn'; }
  else if (m[11]) cls = 'op';
  out += cls ? '<span class="tk-' + cls + '">' + esc(t) + '</span>' : esc(t);
 }
 return out + esc(src.slice(last));
}
document.querySelectorAll('pre > code').forEach(function(c){ if (c.querySelector('span') || /[\u2500-\u257F]/.test(c.textContent)) return; try { c.innerHTML = highlight(c.textContent); } catch (e) {} });
})();
