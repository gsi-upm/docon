from utils import *

if __name__ == "__main__":
    import argparse
    logging.basicConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o",
                        "--output")
    parser.add_argument("-i",
                        "--infile",
                        help="input file",
                        default=None)
    parser.add_argument("-t",
                        "--template",
                        help="template file",
                        required=True,
                        default=None)
    args = parser.parse_args()
    outfile = sys.stdout
    infile = sys.stdin
    if args.output:
        outfile = args.output
    if args.infile:
        infile = args.infile
    with open(args.template, 'r') as template:
        logger.debug("Output is {}".format(outfile))
        logger.debug("Input is {}".format(infile))
        logger.debug("Template is {}".format(args.template))
        stream = translate_document(infile, template.read())
        stream.dump(outfile)

