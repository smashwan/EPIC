import constants, pandas, pdb, os, fnmatch, logging, pdb, numpy
from sqlalchemy import create_engine
from multiprocessing.dummy import Pool

class EPIC_Output_File():
    """
    Class to read EPIC Output files
    """
    def __init__(self, ftype='', tag=''):
        """
        Constructor
        """
        # Create a sqlite database in the analysis directory
        self.db_name = 'sqlite:///' + constants.anly_dir + os.sep + ftype + '_' + tag + '.db'
        self.engine  = create_engine(self.db_name)
        self.ftype   = ftype
        self.tag     = tag

    def parse_ACY(self, fl):
        df      = pandas.read_csv(constants.sims_dir + os.sep + fl, skiprows=constants.SKIP, skipinitialspace=True,
                                  usecols=constants.ACY_PARAMS, sep=' ')
        time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
        time_df.groupby(lambda x: xrange.year).sum()
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_ANN(self, fl):
        df = pandas.read_csv(constants.sims_dir + os.sep + fl, skiprows=constants.SKIP, skipinitialspace=True,
                             usecols=constants.ANN_PARAMS, sep=' ')
        time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
        time_df.groupby(lambda x: xrange.year).sum()
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_DGN(self, fl):
        df      = pandas.read_csv(constants.sims_dir + os.sep + fl, skiprows=constants.SKIP, delim_whitespace=True,
                                  usecols=constants.DGN_PARAMS, parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                                  date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))
        time_df = df.ix[constants.START_YR:constants.END_YR]
        time_df = time_df.groupby(time_df.index.map(lambda x: x.year)).max()
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_ATG(self, fl):
        df      = pandas.read_csv(constants.sims_dir + os.sep + constants.GET_PARAMS[0] + os.sep + fl, skiprows=constants.SKIP, skipinitialspace=True,
                                  usecols=constants.ATG_PARAMS, sep=' ')
        time_df = df[(df.Y >= int(constants.START_YR)) & (df.Y <= int(constants.END_YR))]
        pdb.set_trace()
        time_df.groupby(lambda x: xrange.Y).sum()
        time_df['site'] = fl[:-4]

        return fl[:-4], time_df.BIOM.max() - time_df.RWT.max()
        #pdb.set_trace()
        #time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def collect_epic_output(self, fls):
        pool = Pool(constants.max_threads)
        if(self.ftype == 'DGN'):
            pool.map(self.parse_DGN, fls)
        elif(self.ftype == 'ACY'):
            pool.map(self.parse_ACY, fls)
        elif(self.ftype == 'ANN'):
            pool.map(self.parse_ANN, fls)
        elif(self.ftype == 'ATG'):
            self.parse_ATG(fls[0])
            #pool.map(self.parse_ATG, fls)
        else:
            logging.info( 'Wrong file type')

    def sql_to_csv(self):
        fls = ''
        dfs = pandas.DataFrame(index=numpy.arange(0, len(fls)), columns=['site','biom_rwt'])

        for idx, f in enumerate(fls):
            st, val = self.parse_ATG(f)
            dfs.loc[idx] = [st, val]
        dfs.to_csv('C:\\Users\\ritvik\\Documents\PhD\\Projects\\Lake_States\\EPIC\\OpenLands_LS\\out_wi.csv')

if __name__ == '__main__':
    epic_fl_types = constants.GET_PARAMS

    for fl_name in epic_fl_types:
        list_fls = fnmatch.filter(os.listdir(constants.sims_dir + os.sep + constants.GET_PARAMS[0] + os.sep), '*.' + fl_name)

        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        obj.collect_epic_output(list_fls)
