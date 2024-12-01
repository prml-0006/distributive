import logging
import os

import pandas as pd

import config
import src.elements.s3_parameters as s3p
import src.functions.directories
import src.functions.objects


class Bullet:
    """
    Description<br>
    ------------<br>
    Prepares the data for the <b>False Negative Rate</b> & <b>False Positive Rate</b> bullet graphs.
    """

    def __init__(self, s3_parameters: s3p.S3Parameters):
        """


        :param s3_parameters: The overarching S3 (Simple Storage Service) parameters
                              settings of this project, e.g., region code name, buckets, etc.
        """

        self.__s3_parameters = s3_parameters

        # Configurations
        self.__configurations = config.Config()

        # The directory wherein the data files, for the spider graphs, are stored.
        self.__path = os.path.join(self.__configurations.card_, 'bullet')
        src.functions.directories.Directories().create(path=self.__path)

        # An instance for reading & writing JSON (JavaScript Object Notation) files.
        self.__objects = src.functions.objects.Objects()

        # The metrics in focus.
        self.__names = {'fnr': 'False Negative Rate', 'fpr': 'False Positive Rate'}

    def __limits(self):

        frame = pd.read_json(
            path_or_buf=f's3://{self.__s3_parameters.configurations}/limits/error.json', orient='index')

        frame = frame[self.__names.keys()]
        frame.rename(columns=self.__names, inplace=True)

        return frame

    def __save(self, nodes: dict, name: str):
        """

        :param nodes: The dictionary of values for the spider graph
        :param name: The name of the file; filename & extension.
        :return:
        """

        message = self.__objects.write(nodes=nodes, path=os.path.join(self.__path, name))

        return message

    def exc(self, blob: pd.DataFrame):
        """

        :param blob:
        :return:
        """

        derivations = blob.copy()

        # The unique tag categories
        categories = derivations['category'].unique()

        # The tag & category values are required for data structuring
        derivations.set_index(keys=['tag'], drop=False, inplace=True)

        # Limits
        limits = self.__limits()

        # Hence
        for category in categories:

            name = self.__configurations.definition[category]

            # The instances of the category
            excerpt: pd.DataFrame = derivations.loc[derivations['category'] == category, self.__names.keys()]
            excerpt.rename(columns=self.__names, inplace=True)

            # The dictionary of the instances
            nodes = excerpt.to_dict(orient='split')
            nodes['target'] = limits.loc[category, nodes['columns']].to_list()
            logging.info(nodes)

            # Save
            message = self.__save(nodes=nodes, name=f'{name}.json')
            logging.info(message)
