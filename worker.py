# worker.py
import os
import time
import logging
from datetime import datetime
from pathlib import Path

from config.config_manager import ConfigManager
from database import db, init_db
from main import create_app

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('worker')

def process_pending_analyses():
    """Processa análises pendentes na fila"""
    from models.analysis import Analysis
    
    try:
        # Buscar análises pendentes
        with app.app_context():
            pending_analyses = Analysis.query.filter_by(status='pending').all()
            
            if pending_analyses:
                logger.info(f"Encontradas {len(pending_analyses)} análises pendentes")
                
                for analysis in pending_analyses:
                    logger.info(f"Processando análise ID: {analysis.id}")
                    
                    try:
                        # Atualizar status
                        analysis.status = 'processing'
                        db.session.commit()
                        
                        # Processar análise (simulação)
                        time.sleep(2)  # Simulando processamento
                        
                        # Atualizar status para concluído
                        analysis.status = 'completed'
                        analysis.completed_at = datetime.utcnow()
                        db.session.commit()
                        
                        logger.info(f"Análise ID: {analysis.id} concluída com sucesso")
                    except Exception as e:
                        logger.error(f"Erro ao processar análise ID: {analysis.id}: {str(e)}")
                        
                        # Marcar como falha
                        analysis.status = 'failed'
                        analysis.error_message = str(e)
                        db.session.commit()
            else:
                logger.info("Nenhuma análise pendente encontrada")
    except Exception as e:
        logger.error(f"Erro ao processar análises pendentes: {str(e)}")

def cleanup_old_files():
    """Limpa arquivos temporários antigos"""
    try:
        temp_dir = Path('uploads/temp')
        if temp_dir.exists():
            current_time = time.time()
            for file_path in temp_dir.glob('*'):
                # Remover arquivos com mais de 24 horas
                if (current_time - file_path.stat().st_mtime) > 86400:
                    file_path.unlink()
                    logger.info(f"Arquivo temporário removido: {file_path}")
    except Exception as e:
        logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")

if __name__ == "__main__":
    logger.info("Iniciando worker...")
    
    # Criar aplicação Flask
    app = create_app()
    
    # Loop principal do worker
    while True:
        try:
            logger.info("Executando tarefas agendadas...")
            
            # Processar análises pendentes
            process_pending_analyses()
            
            # Limpar arquivos temporários
            cleanup_old_files()
            
            # Aguardar próximo ciclo (a cada 5 minutos)
            logger.info("Aguardando próximo ciclo...")
            time.sleep(300)
        except KeyboardInterrupt:
            logger.info("Worker interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal do worker: {str(e)}")
            # Aguardar um pouco antes de tentar novamente
            time.sleep(60)