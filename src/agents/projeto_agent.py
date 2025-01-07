from typing import Dict, Optional
import logging
import os
import shutil

logger = logging.getLogger(__name__)

class ProjetoAgent:
    def __init__(self):
        self.workspace = "/root/projetos"
        logger.info(f"✓ Workspace configurado em {self.workspace}")
    
    async def criar_projeto(self, nome_projeto: str) -> Dict:
        """Cria um novo projeto com a estrutura básica"""
        try:
            # Define o caminho do projeto
            caminho_projeto = os.path.join(self.workspace, nome_projeto)
            
            # Cria a estrutura de diretórios
            os.makedirs(caminho_projeto, exist_ok=True)
            os.makedirs(os.path.join(caminho_projeto, "src"), exist_ok=True)
            os.makedirs(os.path.join(caminho_projeto, "src", "components"), exist_ok=True)
            os.makedirs(os.path.join(caminho_projeto, "src", "pages"), exist_ok=True)
            os.makedirs(os.path.join(caminho_projeto, "src", "services"), exist_ok=True)
            os.makedirs(os.path.join(caminho_projeto, "src", "types"), exist_ok=True)
            
            # Cria arquivo package.json básico
            package_json = {
                "name": nome_projeto,
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "typescript": "^4.9.5"
                }
            }
            
            with open(os.path.join(caminho_projeto, "package.json"), "w") as f:
                import json
                json.dump(package_json, f, indent=2)
            
            # Cria arquivo tsconfig.json básico
            tsconfig_json = {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "esModuleInterop": True,
                    "allowSyntheticDefaultImports": True,
                    "strict": True,
                    "forceConsistentCasingInFileNames": True,
                    "noFallthroughCasesInSwitch": True,
                    "module": "esnext",
                    "moduleResolution": "node",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx"
                },
                "include": ["src"]
            }
            
            with open(os.path.join(caminho_projeto, "tsconfig.json"), "w") as f:
                json.dump(tsconfig_json, f, indent=2)
            
            return {
                "tipo": "sucesso",
                "resposta": f"✅ Projeto {nome_projeto} criado com sucesso em {caminho_projeto}\n" + \
                           f"📁 Estrutura criada:\n" + \
                           f"  - /src\n" + \
                           f"    - /components\n" + \
                           f"    - /pages\n" + \
                           f"    - /services\n" + \
                           f"    - /types\n" + \
                           f"📝 Arquivos de configuração criados:\n" + \
                           f"  - package.json\n" + \
                           f"  - tsconfig.json"
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar projeto: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Erro ao criar projeto: {str(e)}"
            }
    
    async def criar_pagina(self, nome_projeto: str, nome_pagina: str) -> Dict:
        """Cria uma nova página no projeto"""
        try:
            # Define os caminhos
            caminho_projeto = os.path.join(self.workspace, nome_projeto)
            caminho_pagina = os.path.join(caminho_projeto, "src", "pages", nome_pagina)
            
            # Verifica se o projeto existe
            if not os.path.exists(caminho_projeto):
                return {
                    "tipo": "erro",
                    "resposta": f"❌ Projeto {nome_projeto} não encontrado"
                }
            
            # Cria o diretório da página
            os.makedirs(caminho_pagina, exist_ok=True)
            
            # Cria o arquivo index.tsx
            conteudo_index = f"""import React from 'react';

const {nome_pagina}: React.FC = () => {{
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{nome_pagina}</h1>
      {/* TODO: Adicionar conteúdo da página */}
    </div>
  );
}};

export default {nome_pagina};
"""
            
            with open(os.path.join(caminho_pagina, "index.tsx"), "w") as f:
                f.write(conteudo_index)
            
            return {
                "tipo": "sucesso",
                "resposta": f"✅ Página {nome_pagina} criada em {caminho_pagina}\n" + \
                           f"📝 Arquivos criados:\n" + \
                           f"  - index.tsx"
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar página: {e}")
            return {
                "tipo": "erro",
                "resposta": f"❌ Erro ao criar página: {str(e)}"
            }
