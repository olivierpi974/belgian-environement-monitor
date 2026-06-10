import logging

# deux handlers, StreamHandler + FileHandler, sans le copier-coller de la doc.
#set up logging to file 
def get_logger():
    logger= logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) #envoi que les log du niveau DEBUG et supérieur dans le fichier

    if not logger.handlers:
        # define a console handler which writes INFO messages or higher
        console_handler=logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        
        #define a file handler which writes DEBUG messages or higher
        file_handler=logging.FileHandler(filename='log/pipeline.log')
        file_handler.setLevel(logging.DEBUG)

        #define a formatter for console use with the format to use
        formatter_console=logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

        #tell the handler to use this format
        console_handler.setFormatter(formatter_console)

        #add the handler to the logger. 
        logger.addHandler(console_handler)

        #define a formatter for file use
        formatter_file=logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        file_handler.setFormatter(formatter_file)
        logger.addHandler(file_handler)
    
    return logger


