CKEDITOR.editorConfig = function(config) {
    // Базовые настройки
    config.language = 'ru';
    config.height = 400;
    config.width = '100%';
    config.skin = 'moono-dark';
    
    // Настройка панели инструментов
    config.toolbar = [
        {
            name: 'basicstyles',
            items: [
                'RemoveFormat', 'Undo', 'Redo', 'Preview', '-',
                'Bold', 'Italic', 'Underline', 'Strike', '-',
                'Link', 'Blockquote', 'Code', 'Smiley', 'Spoiler'
            ]
        },
        {
            name: 'paragraph',
            items: [
                'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
                'Indent', 'Outdent', '-',
                'HorizontalRule',
                'NumberedList', 'BulletedList',
                'Subscript', 'Superscript'
            ]
        },
        '/',
        {
            name: 'styles',
            items: [
                'FontSize', 'Font', 'Format',
                'TextColor', 'BGColor'
            ]
        }
    ];

    // Добавляем плагины
    config.extraPlugins = 'justify,font,colorbutton,panelbutton,floatpanel,richcombo,format,indentblock,indent,horizontalrule,smiley,spoiler,blockquote,specialchar';
    
    // Настройки контента
    config.format_tags = 'p;h1;h2;h3;h4;h5;h6;pre';
    config.fontSize_sizes = '8/8px;9/9px;10/10px;11/11px;12/12px;14/14px;16/16px;18/18px;20/20px;22/22px;24/24px;26/26px;28/28px;36/36px;48/48px;72/72px';
    config.font_names = 'Arial/Arial, Helvetica, sans-serif;' +
                       'Comic Sans MS/Comic Sans MS, cursive;' +
                       'Courier New/Courier New, Courier, monospace;' +
                       'Georgia/Georgia, serif;' +
                       'Lucida Sans Unicode/Lucida Sans Unicode, Lucida Grande, sans-serif;' +
                       'Tahoma/Tahoma, Geneva, sans-serif;' +
                       'Times New Roman/Times New Roman, Times, serif;' +
                       'Trebuchet MS/Trebuchet MS, Helvetica, sans-serif;' +
                       'Verdana/Verdana, Geneva, sans-serif';

    // Разрешаем все теги
    config.allowedContent = true;
    
    // Отключаем фильтрацию контента
    config.fillEmptyBlocks = false;

    // Горячие клавиши
    config.keystrokes = [
        [ CKEDITOR.CTRL + 66, 'bold' ],      // Ctrl+B
        [ CKEDITOR.CTRL + 73, 'italic' ],    // Ctrl+I
        [ CKEDITOR.CTRL + 85, 'underline' ], // Ctrl+U
        [ CKEDITOR.CTRL + 90, 'undo' ],      // Ctrl+Z
        [ CKEDITOR.CTRL + 89, 'redo' ]       // Ctrl+Y
    ];

    // Настройки автосохранения
    config.autosave = {
        saveDetectionSelectors: 'form input[type=submit]',
        delay: 10
    };

    // Настройки диалоговых окон
    config.dialog_backgroundCoverColor = '#000';
    config.dialog_backgroundCoverOpacity = 0.7;
    
    // Дополнительные настройки
    config.removeButtons = '';
    config.colorButton_enableMore = true;
    config.colorButton_colors = '000,800000,8B4513,2F4F4F,008080,000080,4B0082,696969,' +
                               'B22222,A52A2A,DAA520,006400,40E0D0,0000CD,800080,808080,' +
                               'F00,FF8C00,FFD700,008000,0FF,00F,EE82EE,A9A9A9,' +
                               'FFA07A,FFA500,FFFF00,00FF00,AFEEEE,ADD8E6,DDA0DD,D3D3D3,' +
                               'FFF0F5,FAEBD7,FFFFE0,F0FFF0,F0FFFF,F0F8FF,E6E6FA,FFF';
}; 