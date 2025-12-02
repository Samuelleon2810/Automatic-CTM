"""
Clase RegistroOperaciones - Patrón Singleton para registro de operaciones
"""
from typing import List, Optional
from datetime import datetime, date
from modelo.Operacion import Operacion


class RegistroOperaciones:
    """
    Singleton para gestionar el registro de todas las operaciones
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegistroOperaciones, cls).__new__(cls)
            cls._instance._inicializado = False
        return cls._instance
    
    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True
    
    @classmethod
    def get_instance(cls) -> 'RegistroOperaciones':
        """
        Obtiene la instancia única del registro
        
        Returns:
            RegistroOperaciones: Instancia singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def registrar(self, operacion: Operacion) -> None:
        """
        Registra una operación en el sistema
        
        Args:
            operacion: Operación a registrar
        """
        from data.database import db
        
        # La operación ya está en la sesión, solo necesitamos asegurarnos
        # de que se persista
        if operacion not in db.session:
            db.session.add(operacion)
        db.session.flush()
    
    def obtener_por_cuenta(self, cuenta: 'Cuenta') -> List[Operacion]:
        """
        Obtiene todas las operaciones de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            
        Returns:
            List[Operacion]: Lista de operaciones
        """
        return Operacion.query.filter_by(
            cuenta_id=cuenta.id
        ).order_by(Operacion.fecha.desc()).all()
    
    def obtener_por_cuenta_y_fecha(self, cuenta: 'Cuenta', 
                                   fecha_inicio: date, 
                                   fecha_fin: date) -> List[Operacion]:
        """
        Obtiene operaciones de una cuenta en un rango de fechas
        
        Args:
            cuenta: Cuenta a consultar
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            
        Returns:
            List[Operacion]: Lista de operaciones
        """
        inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fin = datetime.combine(fecha_fin, datetime.max.time())
        
        return Operacion.query.filter(
            Operacion.cuenta_id == cuenta.id,
            Operacion.fecha >= inicio,
            Operacion.fecha <= fin
        ).order_by(Operacion.fecha.desc()).all()
    
    def obtener_ultimas_n(self, cuenta: 'Cuenta', n: int = 10) -> List[Operacion]:
        """
        Obtiene las últimas N operaciones de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            n: Número de operaciones a obtener
            
        Returns:
            List[Operacion]: Lista de operaciones
        """
        return Operacion.query.filter_by(
            cuenta_id=cuenta.id
        ).order_by(Operacion.fecha.desc()).limit(n).all()
    
    def obtener_por_tipo(self, cuenta: 'Cuenta', tipo: str) -> List[Operacion]:
        """
        Obtiene operaciones de un tipo específico
        
        Args:
            cuenta: Cuenta a consultar
            tipo: Tipo de operación ('retiro', 'deposito', etc.)
            
        Returns:
            List[Operacion]: Lista de operaciones
        """
        return Operacion.query.filter_by(
            cuenta_id=cuenta.id,
            tipo=tipo
        ).order_by(Operacion.fecha.desc()).all()
    
    def obtener_exitosas(self, cuenta: 'Cuenta') -> List[Operacion]:
        """
        Obtiene solo las operaciones exitosas de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            
        Returns:
            List[Operacion]: Lista de operaciones exitosas
        """
        return Operacion.query.filter_by(
            cuenta_id=cuenta.id,
            exitosa=True
        ).order_by(Operacion.fecha.desc()).all()
    
    def obtener_fallidas(self, cuenta: 'Cuenta') -> List[Operacion]:
        """
        Obtiene solo las operaciones fallidas de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            
        Returns:
            List[Operacion]: Lista de operaciones fallidas
        """
        return Operacion.query.filter_by(
            cuenta_id=cuenta.id,
            exitosa=False
        ).order_by(Operacion.fecha.desc()).all()
    
    def obtener_total_retiros_hoy(self, cuenta: 'Cuenta') -> float:
        """
        Obtiene el total retirado hoy de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            
        Returns:
            float: Total retirado hoy
        """
        from data.database import db
        from modelo.Operacion import Retiro
        
        hoy = date.today()
        inicio = datetime.combine(hoy, datetime.min.time())
        fin = datetime.combine(hoy, datetime.max.time())
        
        total = db.session.query(db.func.sum(Retiro.monto)).filter(
            Retiro.cuenta_id == cuenta.id,
            Retiro.fecha >= inicio,
            Retiro.fecha <= fin,
            Retiro.exitosa == True
        ).scalar()
        
        return float(total) if total else 0.0
    
    def obtener_estadisticas_cuenta(self, cuenta: 'Cuenta') -> dict:
        """
        Obtiene estadísticas de operaciones de una cuenta
        
        Args:
            cuenta: Cuenta a analizar
            
        Returns:
            dict: Estadísticas de la cuenta
        """
        from data.database import db
        from modelo.Operacion import Retiro, Deposito
        
        # Total de operaciones
        total_ops = Operacion.query.filter_by(cuenta_id=cuenta.id).count()
        
        # Operaciones exitosas
        exitosas = Operacion.query.filter_by(
            cuenta_id=cuenta.id, 
            exitosa=True
        ).count()
        
        # Total retirado
        total_retirado = db.session.query(db.func.sum(Retiro.monto)).filter(
            Retiro.cuenta_id == cuenta.id,
            Retiro.exitosa == True
        ).scalar() or 0
        
        # Total depositado
        total_depositado = db.session.query(db.func.sum(Deposito.monto)).filter(
            Deposito.cuenta_id == cuenta.id,
            Deposito.exitosa == True
        ).scalar() or 0
        
        return {
            'total_operaciones': total_ops,
            'operaciones_exitosas': exitosas,
            'operaciones_fallidas': total_ops - exitosas,
            'total_retirado': float(total_retirado),
            'total_depositado': float(total_depositado),
            'tasa_exito': (exitosas / total_ops * 100) if total_ops > 0 else 0
        }
    
    def limpiar_operaciones_antiguas(self, dias: int = 365) -> int:
        """
        Limpia operaciones antiguas del sistema
        
        Args:
            dias: Días de antigüedad para eliminar
            
        Returns:
            int: Número de operaciones eliminadas
        """
        from data.database import db
        from datetime import timedelta
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        operaciones_antiguas = Operacion.query.filter(
            Operacion.fecha < fecha_limite
        ).all()
        
        count = len(operaciones_antiguas)
        
        for op in operaciones_antiguas:
            db.session.delete(op)
        
        db.session.commit()
        return count
