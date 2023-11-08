import pygame
import pygame_menu

WINDOW_SIZE:tuple=(1280,840)

clock=pygame.time.Clock()

MY_THEME = pygame_menu.themes.Theme()

MY_THEME.background_color = pygame_menu.BaseImage(image_path='./images/08.jpg')
MY_THEME.border_color = 'grey50'
MY_THEME.border_width=0
MY_THEME.surface_clear_color='white'

MY_THEME.cursor_color = 'black'
MY_THEME.cursor_selection_color=(70,70,70,100)
MY_THEME.cursor_switch_ms=500

MY_THEME.fps=60

MY_THEME.readonly_color='deepskyblue4'
MY_THEME.readonly_selected_color='darkblue'

MY_THEME.scrollarea_outer_margin=(0,0)

MY_THEME.scrollbar_color='grey20'
MY_THEME.scrollbar_cursor= pygame.SYSTEM_CURSOR_HAND
MY_THEME.scrollbar_shadow= True
MY_THEME.scrollbar_shadow_color='honeydew4'
MY_THEME.scrollbar_shadow_offset= 2
MY_THEME.scrollbar_shadow_position=pygame_menu.locals.POSITION_SOUTHWEST
MY_THEME.scrollbar_slider_color='grey30'
MY_THEME.scrollbar_slider_hover_color= 'grey15'
MY_THEME.scrollbar_slider_pad= 0
MY_THEME.scrollbar_thick= 20

MY_THEME.title=True
MY_THEME.title_background_color='grey70'
MY_THEME.title_bar_modify_scrollarea=True
MY_THEME.title_bar_style= pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
MY_THEME.title_close_button=True
MY_THEME.title_close_button_background_color= 'black'
MY_THEME.title_close_button_cursor= pygame.SYSTEM_CURSOR_HAND
MY_THEME.title_fixed= True
MY_THEME.title_float=False
MY_THEME.title_font= pygame_menu.font.FONT_DIGITAL
MY_THEME.title_font_antialias= True
MY_THEME.title_font_color= 'white'
MY_THEME.title_font_shadow=True
MY_THEME.title_font_shadow_color='paleturquoise4'
MY_THEME.title_font_shadow_offset=3
MY_THEME.title_font_shadow_position= pygame_menu.locals.POSITION_SOUTHWEST
MY_THEME.title_font_size= 70
MY_THEME.title_offset= (10,5)
MY_THEME.title_updates_pygame_display= True

MY_THEME.widget_box_arrow_margin=(5,5,5)
MY_THEME.widget_box_arrow_color = 'deepskyblue4'
MY_THEME.widget_box_background_color = 'slategrey'
MY_THEME.widget_box_border_color = 'slategray1'
# MY_THEME.widget_box_border_width=3
# MY_THEME.widget_box_inflate =(20,20)
# MY_THEME.widget_box_margin = (5,5)

MY_THEME.widget_cursor = pygame.SYSTEM_CURSOR_HAND

MY_THEME.widget_alignment= pygame_menu.locals.ALIGN_CENTER
MY_THEME.widget_alignment_ignore_scrollbar_thickness= False
# MY_THEME.widget_background_color=(240,200,48)
# MY_THEME.widget_background_inflate = (50,50)
# MY_THEME.widget_background_inflate_to_selection=True
MY_THEME.widget_border_color ='grey95'
MY_THEME.widget_border_width = 0

MY_THEME.selection_color='whitesmoke'
MY_THEME.widget_font = pygame_menu.font.FONT_MUNRO
MY_THEME.widget_font_antialias = True
MY_THEME.widget_font_background_color = None
MY_THEME.widget_font_background_color_from_menu = False
MY_THEME.widget_font_color = 'grey70'
MY_THEME.widget_font_shadow = True
MY_THEME.widget_font_shadow_color = 'deepskyblue4'
MY_THEME.widget_font_shadow_offset = 2
MY_THEME.widget_font_shadow_position = 'position-southwest'
MY_THEME.widget_font_size = 50

MY_THEME.widget_margin = (0,30)
# MY_THEME.widget_padding (int, float, tuple, list) – Padding of the widget according to CSS rules. It can be a single digit, or a tuple of 2, 3, or 4 elements. Padding modifies widget width/height
MY_THEME.widget_offset = (0,30)

MY_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()

MY_THEME.widget_shadow_aa = 2
MY_THEME.widget_shadow_color = 'midnightblue'
MY_THEME.widget_shadow_radius =15
MY_THEME.widget_shadow_type = 'rectangular'
MY_THEME.widget_shadow_width = 30
MY_THEME.widget_tab_size = 50

def execute_main():
    
    #-------------------------------------------------------------------------
    # Globals
    #-------------------------------------------------------------------------
    global clock
    global MY_THEME
    
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    running = True
    
    #--------------------------------------------------------------------------
    # Create menus : Sub Menu
    #--------------------------------------------------------------------------

    sub_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        title='Sub Menu',
        width=WINDOW_SIZE[0] * 0.75,
        theme=MY_THEME
    )

    sub_menu.add.button(
        'Button',
        print,
        'Sub_menu Button clicked'
        )
    
    sub_menu.add.selector('Selector',
                           [
                               ('1', 'first'),
                               ('2', 'second')],
                           onchange=print,
                           selector_id='sub_menu selector')
    
    """
    # Create menus : Main Menu
    """
    
    main_menu = pygame_menu.Menu(
        'Welcome',
        1200,
        800,
        center_content=True,     
        theme=MY_THEME,
        mouse_motion_selection=False)

    main_menu.add.button(
        'sub menu button',
        sub_menu,
        button_id='sub_menu_btn')

    def on_image_click(message,kwarg_menu=None ):
        btn: Widget = kwarg_menu.get_widget('sub_menu_btn')
        btn.readonly = not btn.readonly
        print(f'Sub Menu button readlonly status : {btn.readonly}')

    # main_menu.add.label(
    #     title='Main label',
    #     label_id='main_label_ID',
    #     max_char=10,
    # )
    
    main_menu.add.text_input(
        'text input')
    
    image=pygame_menu.BaseImage(
        './images/6_star.png'
    ).scale(2,2)
    
    main_menu.add.banner(
        image,
        on_image_click,
        'Image clicked',
        accept_kwargs=True,
        kwarg_menu=main_menu
    )
   
    
    def my_onselect(selected, widget, menu, special_kwarg=''):
        print(f'Select {selected} / {widget} // {menu} /// {special_kwarg}')
    
    def my_onchange(selected,value, special_kwarg=''):
        print(f'Change {selected} / {value} // {special_kwarg}')
    
    def my_onreturn(selected,value, special_kwarg=''):
        print(f'Return {selected} / {value} // {special_kwarg}')
    
    main_menu.add.dropselect(
        'Main dropselect',
        [
            ('first choice','1'),
            ('second choice', '2'),
            ('third choice', '3')],
        onchange=my_onchange,
        onselect=my_onselect,
        onreturn=my_onreturn,
        special_kwarg='test kwarg'
    )
    
    main_menu.add.button(
        'close menu Button',
        main_menu.toggle
    )
    
    main_menu.disable()
    
    # Main loop
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        event_list = pygame.event.get()
        
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu.toggle()
            
        screen.fill('white')

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(
                screen,
                clear_surface=True,
                wait_for_event=False)

        # Flip surface
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__": 
    execute_main()