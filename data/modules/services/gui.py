"""
Modulos de GUI del juego.

Se dividen en dos familias segun si usan una imagen (sprite) o no:

- gui_element : elementos SIN imagen, se dibujan con pygame.draw
                (button, input, text)
- img_element : elementos CON imagen, obtenida via spr_manager
                (img, img_button, img_input)

Ambas familias comparten -a traves de _smooth_move_mixin- el mismo
sistema de movimiento suavizado: move_to() fija un destino y
update_movement() (que hay que llamar una vez por frame) va acercando
el elemento a ese destino recorriendo cada vez una fraccion de la
distancia restante. Al ser proporcional a la distancia, la velocidad
decrece sola a medida que se acerca (desaceleracion progresiva /
ease-out), sin necesidad de llevar velocidad ni aceleracion aparte.

Ademas, button e img_button comparten -a traves de _icon_label_mixin-
la posibilidad de llevar un icono (izquierda o derecha) y/o un texto:
si hay icono, el texto queda pegado a un lado de este (icon_side) y el
conjunto icono+texto se centra en el boton; si no hay icono, el texto
simplemente se centra solo.

Por su parte, input e img_input comparten -a traves de
_text_input_mixin- cursor con posicion editable (clic para ubicarlo,
flechas para moverlo), texto centrado verticalmente, y scroll
horizontal automatico con recorte (clip) para que el texto nunca se
dibuje fuera del campo aunque sea mas largo de lo que entra.

Por ultimo `slide` es un control deslizante (slider) de proposito
general -sirve tanto para volumen como para cualquier valor entre un
minimo y un maximo- con barra, relleno y manija arrastrable.
"""

import pygame

from data.modules.type.item import item
from settings import *


class _smooth_move_mixin:
    """
    Mixin interno (no se instancia solo) que agrega movimiento
    suavizado a cualquier clase que tenga x, y y un metodo _sync_rect().
    """

    def _init_movement(self, x, y):
        self._target_x = x
        self._target_y = y
        self._moving = False
        self._move_smooth = 0.15
        self._move_threshold = 0.5

    def move_to(self, target_x, target_y, smooth=0.15, threshold=0.5):
        """
        Fija un destino (target_x, target_y).
        `smooth` (0-1): fraccion de la distancia restante que se recorre
        cada frame. Mas bajo = mas lento/suave. `threshold`: distancia
        minima para considerar que ya llego. El desplazamiento real
        ocurre en update_movement().
        """
        self._target_x = target_x
        self._target_y = target_y
        self._move_smooth = smooth
        self._move_threshold = threshold
        self._moving = True

    def stop_movement(self):
        """Cancela el movimiento en curso, dejando el elemento donde esta."""
        self._moving = False
        self._target_x, self._target_y = self.x, self.y

    def is_moving(self):
        return self._moving

    def update_movement(self):
        """Debe llamarse una vez por frame. Retorna True mientras se mueve."""
        if not self._moving:
            return False

        dx = self._target_x - self.x
        dy = self._target_y - self.y

        if abs(dx) < self._move_threshold and abs(dy) < self._move_threshold:
            self.x, self.y = self._target_x, self._target_y
            self._moving = False
            self._sync_rect()
            return False

        self.x += dx * self._move_smooth
        self.y += dy * self._move_smooth
        self._sync_rect()
        return True


class _icon_label_mixin:
    """
    Mixin interno (no se instancia solo) que agrega icono + texto a los
    botones (button e img_button).

    - Si hay icono (icon_manager != None) Y texto (txt != None): el
      icono se ubica a un lado (icon_side: "left" o "right") y el
      texto pegado al otro lado, con un espacio "icon_gap" entre
      ambos. El bloque icono+texto completo queda centrado en el rect
      del boton.
    - Si hay solo icono: el icono se centra solo.
    - Si hay solo texto (o ninguno de los dos parametros de icono):
      el texto se centra solo, igual que antes.

    Requiere que la clase que lo use ya tenga self.rect y self.scale
    definidos (es decir, se llama _init_icon_label() despues del
    __init__ de gui_element/img_element), y que sobreescriba
    _sync_rect() llamando a super()._sync_rect() y luego a
    self._layout_icon_text(), para que el icono y el texto se
    reacomoden solos ante cualquier cambio de posicion/escala
    (set_pos, set_scale, move_to/update_movement).
    """

    def _init_icon_label(self, txt=None, font=None, txt_color=None,
                          icon_manager=None, icon_sx=0, icon_sy=0,
                          icon_w=0, icon_h=0, icon_side="left", icon_gap=8):
        self.icon = None
        self.text = None
        self.icon_side = icon_side
        self.icon_gap = icon_gap

        if icon_manager is not None:
            self.icon = img(0, 0, icon_manager, icon_sx, icon_sy, icon_w, icon_h, self.scale)

        if txt is not None:
            self.text = text(0, 0, txt, font, txt_color or (255, 255, 255), self.scale)

        self._layout_icon_text()

    def _layout_icon_text(self):
        # Durante el __init__ de la clase base (gui_element/img_element)
        # ya se llama a _sync_rect() antes de que existan self.icon/self.text.
        if not hasattr(self, "icon") or not hasattr(self, "text"):
            return
        if self.icon is None and self.text is None:
            return

        cx, cy = self.rect.center

        if self.icon is not None and self.text is not None:
            gap = self.icon_gap
            total_w = self.icon.rect.width + gap + self.text.rect.width
            start_x = cx - total_w // 2

            if self.icon_side == "left":
                icon_x = start_x
                text_x = icon_x + self.icon.rect.width + gap
            else:  # "right"
                text_x = start_x
                icon_x = text_x + self.text.rect.width + gap

            self.icon.set_pos(icon_x, cy - self.icon.rect.height // 2)
            self.text.set_pos(text_x, cy - self.text.rect.height // 2)

        elif self.icon is not None:
            self.icon.set_pos(cx - self.icon.rect.width // 2, cy - self.icon.rect.height // 2)

        else:
            self.text.set_pos(cx - self.text.rect.width // 2, cy - self.text.rect.height // 2)

    def _draw_icon_label(self, screen):
        if self.icon is not None:
            self.icon.draw(screen)
        if self.text is not None:
            self.text.draw(screen)


class _text_input_mixin:
    """
    Mixin interno (no se instancia solo) que agrega a los campos de
    texto (input e img_input).
    """

    def _init_text_input(
        self,
        font,
        text="",
        max_len=20,
        padding=8,
        char_filter=None,
        scale=1.0
    ):
        self.font = font
        self.scale = scale

        # Tamaño aproximado de la fuente original
        base_height = font.get_height()
        scaled_height = round(base_height * scale)

        # Escalar usando el tamaño de fuente.
        # Esto conserva las métricas necesarias para cursor/scroll.
        if scale != 1.0:
            self.font = pygame.font.Font(None, scaled_height)

        self.txt = text
        self.max_len = max_len
        self.padding = padding
        self.char_filter = char_filter

        self.active = False
        self.cursor_pos = len(self.txt)
        self.scroll_x = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_delay = 500

    def _char_allowed(self, ch):
        if self.char_filter is None:
            return True
        if self.char_filter == "numbers":
            return ch.isdigit()
        if self.char_filter == "letters":
            return ch.isalpha()
        return True

    def _text_width(self, s):
        return self.font.size(s)[0]

    def get_text(self):
        """Retorna el texto actual como string."""
        return self.txt

    def _set_cursor_from_click(self, mouse_x):
        rel_x = mouse_x - (self.rect.x + self.padding) + self.scroll_x

        best_i, best_dist = 0, abs(rel_x)

        for i in range(1, len(self.txt) + 1):
            dist = abs(
                self._text_width(self.txt[:i]) - rel_x
            )

            if dist < best_dist:
                best_dist, best_i = dist, i

        self.cursor_pos = best_i

    def _update_scroll(self):
        visible_w = max(
            0,
            self.rect.width - 2 * self.padding
        )

        total_w = self._text_width(self.txt)

        if total_w <= visible_w:
            self.scroll_x = 0
            return

        cursor_w = self._text_width(
            self.txt[:self.cursor_pos]
        )

        if cursor_w - self.scroll_x > visible_w:
            self.scroll_x = cursor_w - visible_w

        if cursor_w - self.scroll_x < 0:
            self.scroll_x = cursor_w

        self.scroll_x = max(
            0,
            min(
                self.scroll_x,
                total_w - visible_w
            )
        )

    def _handle_text_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

            if self.active:
                self._set_cursor_from_click(event.pos[0])
                self._update_scroll()

            return

        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.txt = (
                    self.txt[:self.cursor_pos - 1]
                    + self.txt[self.cursor_pos:]
                )
                self.cursor_pos -= 1

        elif event.key == pygame.K_DELETE:
            self.txt = (
                self.txt[:self.cursor_pos]
                + self.txt[self.cursor_pos + 1:]
            )

        elif event.key == pygame.K_LEFT:
            self.cursor_pos = max(
                0,
                self.cursor_pos - 1
            )

        elif event.key == pygame.K_RIGHT:
            self.cursor_pos = min(
                len(self.txt),
                self.cursor_pos + 1
            )

        elif event.key == pygame.K_HOME:
            self.cursor_pos = 0

        elif event.key == pygame.K_END:
            self.cursor_pos = len(self.txt)

        elif event.key == pygame.K_RETURN:
            self.active = False

        elif (
            event.unicode
            and event.unicode.isprintable()
            and len(self.txt) < self.max_len
            and self._char_allowed(event.unicode)
        ):
            self.txt = (
                self.txt[:self.cursor_pos]
                + event.unicode
                + self.txt[self.cursor_pos:]
            )
            self.cursor_pos += 1

        self._update_scroll()

    def update(self, dt):
        self.cursor_timer += dt

        if self.cursor_timer >= self.cursor_delay:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def _draw_text_input(self, screen):
        self.text_surf = self.font.render(
            self.txt,
            True,
            (255, 255, 255)
        )
        text_r = self.text_surf.get_rect()

        text_y = (
            self.rect.centery
            - self.text_surf.get_height() // 2
        )

        prev_clip = screen.get_clip()
        screen.set_clip(self.rect)

        screen.blit(
            self.text_surf,
            (
                self.rect.x + self.padding - self.scroll_x,
                text_y
            )
        )

        if self.active and self.cursor_visible:
            cursor_x = (
                self.rect.x
                + self.padding
                - self.scroll_x
                + self._text_width(
                    self.txt[:self.cursor_pos]
                )
            )

            pygame.draw.line(
                screen,
                (255, 255, 255),
                (cursor_x, self.rect.y + 10*self.scale),
                (cursor_x, self.rect.bottom - 10*self.scale),
                2
            )

        screen.set_clip(prev_clip)



# ============================================================
#  CLASES BASE
# ============================================================

class gui_element(_smooth_move_mixin):
    """
    Base para elementos de GUI SIN imagen: se dibujan con formas
    (pygame.draw). Comparte posicion, tamaño base (w, h) y un
    multiplicador de escala (scale) que afecta el rect final.
    """

    def __init__(self, x, y, w, h, scale=1.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.scale = scale

        self.rect = pygame.Rect(0, 0, self._scaled_w, self._scaled_h)
        self._sync_rect()

        self._init_movement(x, y)

    @property
    def _scaled_w(self):
        return max(1, int(self.w * self.scale))

    @property
    def _scaled_h(self):
        return max(1, int(self.h * self.scale))

    def set_scale(self, scale):
        self.scale = scale
        self._sync_rect()

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self._sync_rect()

    def _sync_rect(self):
        self.rect.size = (self._scaled_w, self._scaled_h)
        self.rect.topleft = (round(self.x), round(self.y))


class img_element(_smooth_move_mixin):
    """
    Base para elementos de GUI CON imagen, obtenida desde un
    spr_manager (recorte de un spritesheet). Comparte posicion, tamaño
    base, escala y el mismo sistema de movimiento suavizado.
    """

    def __init__(self, x, y, sprite_manager, sx, sy, w, h, scale=1.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.scale = scale

        self.sprite_manager = sprite_manager
        self.sx = sx
        self.sy = sy

        self.image = self._load_image()
        self.rect = self.image.get_rect()
        self._sync_rect()

        self._init_movement(x, y)

    def _load_image(self):
        base = self.sprite_manager.get_sprite(self.sx, self.sy, self.w, self.h)
        w = max(1, int(self.w * self.scale))
        h = max(1, int(self.h * self.scale))
        if (w, h) != base.get_size():
            base = pygame.transform.scale(base, (w, h))
        return base

    def set_scale(self, scale):
        self.scale = scale
        self.image = self._load_image()
        self._sync_rect()

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self._sync_rect()

    def _sync_rect(self):
        self.rect.size = self.image.get_size()
        self.rect.topleft = (round(self.x), round(self.y))


# ============================================================
#  ELEMENTOS SIN IMAGEN
# ============================================================

class text(gui_element):
    """Texto renderizado con una font (sin imagen)."""

    def __init__(self, x, y, txt, font, color=(255, 255, 255), scale=1.0):
        self.txt = txt
        self.font = font
        self.color = color
        raw = self.font.render(self.txt, True, self.color)

        super().__init__(x, y, raw.get_width(), raw.get_height(), scale)
        self._raw_surf = raw
        self._surf = self._scale_surf()

    def _scale_surf(self):
        if self.scale == 1.0:
            return self._raw_surf
        return pygame.transform.smoothscale(self._raw_surf, (self._scaled_w, self._scaled_h))

    def set_text(self, txt):
        self.txt = txt
        self._raw_surf = self.font.render(self.txt, True, self.color)
        self.w, self.h = self._raw_surf.get_size()
        self._surf = self._scale_surf()
        self._sync_rect()

    def set_scale(self, scale):
        self.scale = scale
        self._surf = self._scale_surf()
        self._sync_rect()

    def draw(self, screen):
        screen.blit(self._surf, self.rect)


class button(gui_element, _icon_label_mixin):
    """
    Boton rectangular de color solido (sin imagen).

    Puede llevar texto (txt/font/txt_color), un icono (icon_manager +
    icon_sx/icon_sy/icon_w/icon_h, recortado de un spr_manager como
    cualquier img) o ambos. Si tiene icono, este va a la izquierda o
    derecha del boton segun icon_side ("left"/"right") y el texto
    queda pegado al lado contrario; el conjunto se centra en el
    boton. Si no hay icono, el texto (si existe) se centra solo.
    """

    def __init__(self, x, y, w, h, scale=1.0, border_rad=0,
                 color=red, hovcolor=green, clickcolor=blue, alpha=0,
                 txt=None, font=None, txt_color=None,
                 icon_manager=None, icon_sx=0, icon_sy=0, icon_w=0, icon_h=0,
                 icon_side="left", icon_gap=8):
        super().__init__(x, y, w, h, scale)

        self.b_rad = border_rad
        self.alpha = alpha
        self.cstate = [color, hovcolor, clickcolor]
        self.currentcolor = self.cstate[0]
        self.clicked = False

        self._init_icon_label(txt, font, txt_color, icon_manager, icon_sx, icon_sy,
                               icon_w, icon_h, icon_side, icon_gap)

    def _sync_rect(self):
        super()._sync_rect()
        self._layout_icon_text()

    def event(self):
        action = False
        mpos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action

    def update_color(self):
        self.currentcolor = self.cstate[0]
        mpos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mpos):
            self.currentcolor = self.cstate[1]
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.currentcolor = self.cstate[2]

    def draw(self, screen):
        pygame.draw.rect(screen, self.currentcolor, self.rect, border_radius=self.b_rad)
        self._draw_icon_label(screen)


class input(gui_element, _text_input_mixin):
    """
    Campo de texto editable, sin imagen de fondo.

    El cursor se puede ubicar con un clic (queda en el caracter mas
    cercano al punto donde se hizo clic) o mover con las flechas; el
    texto se centra verticalmente y, si es mas largo de lo que entra
    en el campo, se recorta y se hace scroll automatico para que el
    cursor siempre sea visible.

    char_filter opcional: None (default, sin restriccion), "numbers"
    (solo digitos) o "letters" (solo letras).
    """

    def __init__(self, x, y, w, h, font, scale=1.0, border_rad=0,
                 color=red, hovcolor=green, clickcolor=blue, alpha=0, text="",
                 char_filter=None, txt_scale: float = 1.0):
        super().__init__(x, y, w, h, scale)

        self.b_rad = border_rad
        self.alpha = alpha
        self.cstate = [color, hovcolor, clickcolor]
        self.currentcolor = self.cstate[0]

        self._init_text_input(font, text, padding=10, char_filter=char_filter, scale=txt_scale)

    def event(self, event):
        self._handle_text_event(event)

    def update_color(self):
        self.currentcolor = self.cstate[1] if self.rect.collidepoint(pygame.mouse.get_pos()) else self.cstate[0]

    def draw(self, screen):
        pygame.draw.rect(screen, self.currentcolor, self.rect, border_radius=self.b_rad)
        self._draw_text_input(screen)


class slide(gui_element):
    """
    Slider horizontal sin imagen (barra + relleno + manija), de
    proposito general: sirve para volumen o para cualquier valor
    entre min_val y max_val. Se puede arrastrar la manija o hacer
    clic en cualquier punto de la barra para saltar directo a ese
    valor.
    """

    def __init__(self, x, y, w, h, min_val=0, max_val=100, value=None, scale=1.0,
                 border_rad=0, track_color=(80, 80, 80), fill_color=green,
                 handle_color=(255, 255, 255), handle_radius=None):
        super().__init__(x, y, w, h, scale)

        self.min_val = min_val
        self.max_val = max_val
        self.value = value if value is not None else min_val

        self.b_rad = border_rad
        self.track_color = track_color
        self.fill_color = fill_color
        self.handle_color = handle_color
        self.handle_radius = handle_radius or max(6, self.rect.height // 2 + 2)

        self.dragging = False

    def _value_to_x(self):
        span = self.max_val - self.min_val
        ratio = 0 if span == 0 else (self.value - self.min_val) / span
        ratio = min(1.0, max(0.0, ratio))
        return self.rect.x + ratio * self.rect.width

    def _x_to_value(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / self.rect.width if self.rect.width else 0
        ratio = min(1.0, max(0.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def set_value(self, value):
        self.value = min(self.max_val, max(self.min_val, value))

    def get_value(self):
        return self.value

    def event(self):
        """Debe llamarse una vez por frame. Retorna True el frame en que el valor cambia."""
        changed = False
        mx, my = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        handle_rect = pygame.Rect(0, 0, self.handle_radius * 2, self.handle_radius * 2)
        handle_rect.center = (self._value_to_x(), self.rect.centery)

        if pressed:
            if not self.dragging and (handle_rect.collidepoint(mx, my) or self.rect.collidepoint(mx, my)):
                self.dragging = True

            if self.dragging:
                new_value = self._x_to_value(mx)
                if new_value != self.value:
                    self.value = new_value
                    changed = True
        else:
            self.dragging = False

        return changed

    def draw(self, screen):
        pygame.draw.rect(screen, self.track_color, self.rect, border_radius=self.b_rad)

        fill_w = max(0, min(self.rect.width, self._value_to_x() - self.rect.x))
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(fill_w), self.rect.height)
            pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=self.b_rad)

        pygame.draw.circle(screen, self.handle_color, (round(self._value_to_x()), self.rect.centery), self.handle_radius)


# ============================================================
#  ELEMENTOS CON IMAGEN (spr_manager)
# ============================================================

class img(img_element):
    """Imagen simple, sin interaccion."""

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class img_button(img_element, _icon_label_mixin):
    """
    Boton con imagen de fondo (spr_manager).

    Igual que `button`, admite texto (txt/font/txt_color) y/o un
    icono propio (icon_manager + icon_sx/icon_sy/icon_w/icon_h),
    distinto de la imagen de fondo del boton. Con icono, el texto
    queda pegado al lado contrario segun icon_side; sin icono, el
    texto se centra solo.
    """

    def __init__(self, x, y, sprite_manager, sx, sy, w, h, scale=1.0,
                 txt=None, font=None, txt_color=None, icon_sx=0, icon_sy=0, icon_w=0, icon_h=0,
                 icon_side="left", icon_gap=8):
        super().__init__(x, y, sprite_manager, sx, sy, w, h, scale)
        self.clicked = False

        self._init_icon_label(txt, font, txt_color, sprite_manager, icon_sx, icon_sy,
                               icon_w, icon_h, icon_side, icon_gap)

    def _sync_rect(self):
        super()._sync_rect()
        self._layout_icon_text()

    def event(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_icon_label(screen)


class slot(img_element):
    def __init__(self, x, y, sprite_manager, sx, sy, w, h, item: item=None, amount=0, scale=1, font=None, txt_color=None):
        super().__init__(x, y, sprite_manager, sx, sy, w, h, scale)
        self.clicked = False
        
        self.item = item
        self.amount = amount
        self.amount = min(100, max(0, self.amount))
        self.amount_txt = text(self.x + w-16, self.y + h-12, str(amount), font, txt_color, 1)

    def change_amount(self, amount):
        self.amount += amount
        if self.amount > 0:
            self.amount_txt.set_text(str(self.amount))
        else:
            self.item = None

    def add_item(self, item):
        if self.item is None:
            self.item = item

    def event(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.item is not None:
            self.item.rect.x, self.item.rect.y = self.x + 16, self.y + 16
            self.amount_txt.set_pos(self.x + 64 - 20, self.y + 64 - 24)
            self.item.draw(screen)
            self.amount_txt.draw(screen)
        

class img_input(img_element, _text_input_mixin):
    """
    Campo de texto editable con un sprite de fondo (spr_manager).

    Mismo comportamiento de cursor/scroll/recorte que `input` (via
    _text_input_mixin), solo cambia el fondo, que es una imagen en
    vez de un rectangulo dibujado.

    char_filter opcional: None (default, sin restriccion), "numbers"
    (solo digitos) o "letters" (solo letras).
    """

    def __init__(self, x, y, sprite_manager, sx, sy, w, h, font, scale=1.0, text="",
                 char_filter=None, txt_scale: float = 1.0):
        super().__init__(x, y, sprite_manager, sx, sy, w, h, scale)
        self._init_text_input(font, text, padding=12, char_filter=char_filter, scale=txt_scale)

    def event(self, event):
        self._handle_text_event(event)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_text_input(screen)


class panel(_smooth_move_mixin):
    """
    Caja de GUI armada con un spritesheet tipo "9-slice": una fila de
    3 piezas para arriba (esquina/borde/esquina), otra para el medio
    (borde izq. / centro / borde der., que se repiten para cubrir el
    alto) y otra para abajo -exactamente el mismo criterio que ya
    tenias en tu bg_gui, solo que aca la posicion en pantalla de cada
    baldosa se calcula sola a partir de fila/columna en vez de
    tipearla a mano.

    - tile: tamaño en px de cada baldosa (tanto en el sheet como en
      pantalla, antes de aplicar `scale`).
    - cols/rows: cuantas baldosas mide la caja COMPLETA, esquinas
      incluidas (cols=5, rows=6 con tile=32 da una caja de 160x192px,
      igual a la que armaste a mano).
    - top_sy/mid_sy/bottom_sy: coordenada Y en el sheet de la fila de
      arriba / del medio (bordes que se repiten) / de abajo.
    - left_sx/mid_sx/right_sx: coordenada X en el sheet de la columna
      izquierda / del medio (bordes que se repiten) / derecha.
    - fill=False (default) deja el centro transparente -para que se
      siga viendo lo que haya atras, como tu fondo estrellado-;
      fill=True tambien dibuja el centro repitiendo la pieza
      (mid_sx, mid_sy).

    Se comporta como cualquier otro elemento de gui.py: move_to() /
    set_pos() / update_movement() mueven TODAS las piezas juntas
    (nunca hay que tocarlas una por una), y draw() las dibuja todas.
    """

    def __init__(self, x, y, sprite_manager, tile, cols, rows,
                 top_sy, mid_sy, bottom_sy, left_sx, mid_sx, right_sx,
                 fill=False, scale=1.0):
        self.x, self.y = x, y
        self.sprite_manager = sprite_manager
        self.tile = tile
        self.cols = cols
        self.rows = rows
        self.scale = scale

        self.top_sy, self.mid_sy, self.bottom_sy = top_sy, mid_sy, bottom_sy
        self.left_sx, self.mid_sx, self.right_sx = left_sx, mid_sx, right_sx
        self.fill = fill

        self.cells = self._build_cells()
        self._init_movement(x, y)

    @property
    def step(self):
        """Distancia en px entre una baldosa y la siguiente (ya escalada)."""
        return self.tile * self.scale

    @property
    def width(self):
        return self.cols * self.step

    @property
    def height(self):
        return self.rows * self.step

    def _sy_for_row(self, row):
        if row == 0:
            return self.top_sy
        if row == self.rows - 1:
            return self.bottom_sy
        return self.mid_sy

    def _sx_for_col(self, col):
        if col == 0:
            return self.left_sx
        if col == self.cols - 1:
            return self.right_sx
        return self.mid_sx

    def _build_cells(self):
        cells = []
        for row in range(self.rows):
            sy = self._sy_for_row(row)
            row_cells = []
            for col in range(self.cols):
                sx = self._sx_for_col(col)

                is_center = 0 < row < self.rows - 1 and 0 < col < self.cols - 1
                if is_center and not self.fill:
                    row_cells.append(None)
                    continue

                px = self.x + col * self.step
                py = self.y + row * self.step
                row_cells.append(img(px, py, self.sprite_manager, sx, sy, self.tile, self.tile, self.scale))

            cells.append(row_cells)
        return cells

    def _sync_rect(self):
        for row, row_cells in enumerate(self.cells):
            for col, cell in enumerate(row_cells):
                if cell is not None:
                    cell.set_pos(self.x + col * self.step, self.y + row * self.step)

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self._sync_rect()

    def set_scale(self, scale):
        self.scale = scale
        for row_cells in self.cells:
            for cell in row_cells:
                if cell is not None:
                    cell.set_scale(scale)
        self._sync_rect()

    def draw(self, screen):
        for row_cells in self.cells:
            for cell in row_cells:
                if cell is not None:
                    cell.draw(screen)