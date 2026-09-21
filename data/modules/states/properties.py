class prop:
    @staticmethod
    def set_value(element, value):
        element = value
        return element


class flamable(prop):
    def __init__(self, flam_val: float=0):
        """
        Inflamabilidad.
        Su valor se ve en porcentajes, como 1 el 100% y 0 un 0%.
        
        Args:
            flam_val: porcentaje de inflamabilidad en decimal, del 0 al 1 
        """
        self.flameability = 0
        self.flameability = max(0, min(1, flam_val))

    def flam(self) -> float:
        """
        Devuelve su propiedad en decimal

        Returns:
            flam: float -> valor de inflamavilidad en decimal
        """
        return self.flameability

    def flam_percent(self) -> str:
        """
        Devuelve su propiedad en porcentaje

        Returns:
            flam: str -> valor de explosividad porcental
        """
        return f'{int(self.flameability*100)}%'
    

class explosiveness(prop):
    def __init__(self, expl_val: float = 0):
        """
        Explosividad.
        Su valor se ve en porcentajes, como 1 el 100% y 0 un 0%.
        
        Args:
            expl_val: porcentaje de explosividad en decimal, del 0 al 1 
        """
        self.explosiveness = max(0, min(1, expl_val))

    def explosiveness(self) -> float:
        """
        Devuelve su propiedad en decimal

        Returns:
            explosiveness: float -> valor de explosividad en decimal
        """
        return self.explosiveness
    
    def explosiveness_percent(self) -> str:
        """
        Devuelve su propiedad en porcentaje

        Returns:
            explosividad: str -> valor de explosividad porcental
        """
        return f'{int(self.explosiveness*100)}%'

    


class electric(prop):
    def __init__(self, elec_val: float = 0):
        """
        Capacidad de conductividad electrica.
        Su valor se ve en porcentajes, como 1 el 100% y 0 un 0%.
        
        Args:
            elec_val: porcentaje de inflamabilidad en decimal, del 0 al 1 
        """
        self.electric = max(0, min(1, elec_val))

    def electric(self) -> float:
        """
        Devuelve su propiedad en decimal

        Returns:
            electric: float -> valor de capacidad de conducción electrica en decimal
        """
        return self.electric

    def electric_percent(self) -> str:
        """
        Devuelve su propiedad en porcentaje

        Returns:
            electric: str -> valor de capacidad de conducción electrica porcental
        """
        return f'{int(self.electric*100)}%'
