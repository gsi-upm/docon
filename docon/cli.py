from utils import *

def run_cli():
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
    parser.add_argument("-u",
                        "--baseuri",
                        help="base URI",
                        required=False,
                        default="http://www.eurosentiment.eu/ns#")
    args = parser.parse_args()
    outfile = sys.stdout
    infile = sys.stdin
    if args.output:
        outfile = args.output
    if args.infile:
        infile = args.infile
    with codecs.open(args.template, 'r', encoding="utf-8") as template:
        logger.debug("Output is {}".format(outfile))
        logger.debug("Input is {}".format(infile))
        logger.debug("Template is {}".format(args.template))
        stream = translate_document(infile, template.read(), {"baseuri": args.baseuri})
        stream.dump(outfile, encoding="utf-8")

if __name__ == "__main__":
    run_cli()
