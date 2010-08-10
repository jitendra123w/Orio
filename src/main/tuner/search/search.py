#
# The search engine used for search space exploration
#
import sys, math
from main.util.messages import err, debug

class Search:
    '''The search engine used to explore the search space '''

    MAXFLOAT = float('inf')

    #----------------------------------------------------------
    
    def __init__(self, params):
        '''To instantiate a search engine'''

        # the class variables that are essential to know when developing a new search engine subclass
        if 'search_time_limit' in params.keys(): self.time_limit = params['search_time_limit']
        else: self.time_limit = -1
        if 'search_total_runs' in params.keys(): self.total_runs = params['search_total_runs']
        else: self.total_runs = -1
        if 'search_opts' in params.keys(): self.search_opts = params['search_opts']
        else: self.search_opts = {}
        if 'axis_names' in params.keys(): 
            self.total_dims = len(params['axis_names'])
        else: 
            err('the search space was not defined correctly, missing axis_names parameter')
        if 'axis_val_ranges' in params.keys(): 
            self.dim_uplimits = [len(r) for r in params['axis_val_ranges']]
        else: 
            err('the search space was not defined correctly, missing axis_val_ranges parameter')
            
        self.space_size = 0
        if self.total_dims > 0:
            self.space_size = reduce(lambda x,y: x*y, self.dim_uplimits, 1)
        if 'cmd_line_opts' in params.keys(): self.verbose = params['cmd_line_opts'].verbose
        else: self.verbose = False
        if 'use_parallel_search' in params.keys(): self.use_parallel_search = params['use_parallel_search']
        else: self.use_parallel_search = False
        if 'ptdriver' in params.keys(): self.num_procs = params['ptdriver'].num_procs
        else: self.num_procs = 1
        
        # the class variables that may be ignored when developing a new search engine subclass
        if 'cfrags' in params.keys(): self.cfrags = params['cfrags']
        else: self.cfrags = None
        if 'axis_names' in params.keys(): self.axis_names = params['axis_names']
        else: self.axis_names = None
        if 'axis_val_ranges' in params.keys(): self.axis_val_ranges = params['axis_val_ranges']
        else: self.axis_val_ranges = None
        if 'pparam_constraint' in params.keys(): self.constraint = params['pparam_constraint']
        else: self.constraint = 'None'
        if 'cmd_line_opts' in params.keys(): self.cmd_line_opts = params['cmd_line_opts']
        else: self.cmd_line_opts = None
        if 'ptcodegen' in params.keys(): self.ptcodegen = params['ptcodegen']
        else: self.ptcodegen = None
        if 'ptdriver' in params.keys(): self.ptdriver = params['ptdriver']
        else: self.ptdriver = None
        if 'odriver' in params.keys(): self.odriver = params['odriver']
        else: self.odriver = None
        
        self.perf_cost_records = {}
        
    #----------------------------------------------------------

    def searchBestCoord(self):
        '''
        Explore the search space and return the coordinate that yields the best performance
        (i.e. minimum performance cost).
        
        This is the function that needs to be implemented in each new search engine subclass.
        '''
        raise NotImplementedError('%s: unimplemented abstract function "searchBestCoord"' %
                                  self.__class__.__name__)
    
    #----------------------------------------------------------

    def search(self):
        '''To initiate the search process and return the best performance parameters'''

        # if the search space is empty
        if self.total_dims == 0:
            return {}

        # find the coordinate resulting in the best performance
        best_coord = self.searchBestCoord()

        # if no best coordinate can be found
        if best_coord == None:
            err ('the search cannot find a valid set of performance parameters. ' +
                 'the search time limit might be too short, or the performance parameter ' +
                 'constraints might prune out the entire search space.')
           

        # get the performance cost of the best parameters
        best_perf_cost = self.getPerfCost(best_coord)

        # convert the coordinate to the corresponding performance parameters
        best_perf_params = self.coordToPerfParams(best_coord)

        # return the best performance parameters
        return (best_perf_params, best_perf_cost)

    #----------------------------------------------------------

    def coordToPerfParams(self, coord):
        '''To convert the given coordinate to the corresponding performance parameters'''

        # get the performance parameters that correspond the given coordinate
        perf_params = {}
        for i in range(0, self.total_dims):
            ipoint = coord[i]
            perf_params[self.axis_names[i]] = self.axis_val_ranges[i][ipoint]

        # return the obtained performance parameters
        return perf_params

    #----------------------------------------------------------

    def getPerfCost(self, coord):
        '''
        To empirically evaluate the performance cost of the code corresponding to the given coordinate
        '''

        perf_costs = self.getPerfCosts([coord])
        [perf_cost,] = perf_costs.values()
        return perf_cost

    #----------------------------------------------------------

    def getPerfCosts(self, coords):
        '''
        Empirically evaluate the performance costs of the codes corresponding the given coordinates
        @param coords:  all search space coordinates
        '''

        # initialize the performance costs mapping
        perf_costs = {}

        # filter out all invalid coordinates and previously evaluated coordinates
        uneval_coords = []
        for coord in coords:
            coord_key = str(coord)

            # if the given coordinate is out of the search space
            is_out = False
            for i in range(0, self.total_dims):
                if coord[i] < 0 or coord[i] >= self.dim_uplimits[i]:
                    is_out = True
                    break
            if is_out:
                perf_costs[coord_key] = self.MAXFLOAT
                continue

            # if the given coordinate has been computed before
            if coord_key in self.perf_cost_records:
                perf_costs[coord_key] = self.perf_cost_records[coord_key]
                continue

            # get the performance parameters
            perf_params = self.coordToPerfParams(coord)
        
            # test if the performance parameters are valid
            try:
                is_valid = eval(self.constraint, perf_params)
            except Exception, e:
                err('failed to evaluate the constraint expression: "%s"\n%s %s' % (self.constraint,e.__class__.__name__, e))

            # if invalid performance parameters
            if not is_valid:
                perf_costs[coord_key] = self.MAXFLOAT
                continue

            # store all unevaluated coordinates
            uneval_coords.append(coord)

        # check the unevaluated coordinates
        if len(uneval_coords) == 0:
            return perf_costs

        # get the transformed code for each corresponding coordinate
        code_map = {}
        for coord in uneval_coords:
            coord_key = str(coord)
            perf_params = self.coordToPerfParams(coord)
            transformed_code_seq = self.odriver.optimizeCodeFrags(self.cfrags, perf_params)
            if len(transformed_code_seq) != 1:
                err('internal error: the optimized annotation code cannot contain multiple versions')
                sys.exit(1)
            transformed_code, _ = transformed_code_seq[0]
            code_map[coord_key] = transformed_code
        debug("search.py: about to test the following code segments (code_map):\n%s" % code_map)

        # evaluate the performance costs for all coordinates
        test_code = self.ptcodegen.generate(code_map)
        new_perf_costs = self.ptdriver.run(test_code)

        # remember the performance cost of previously evaluated coordinate
        self.perf_cost_records.update(new_perf_costs.items())

        # merge the newly obtained performance costs
        perf_costs.update(new_perf_costs.items())
        
        # return the performance cost
        return perf_costs

    #----------------------------------------------------------

    def factorial(self, n):
        '''Return the factorial value of the given number'''
        return reduce(lambda x,y: x*y, range(1, n+1), 1)

    def roundInt(self, i):
        '''Proper rounding for integer'''
        return int(round(i))

    def getRandomInt(self, lbound, ubound):
        '''To generate a random integer N such that lbound <= N <= ubound'''
        from random import randint

        if lbound > ubound:
            print ('internal error: the lower bound of genRandomInt must not be ' +
                   'greater than the upper bound')
            sys.exit()
        return randint(lbound, ubound)

    def getRandomReal(self, lbound, ubound):
        '''To generate a random real number N such that lbound <= N < ubound'''
        from random import uniform

        if lbound > ubound:
            print ('internal error: the lower bound of genRandomReal must not be ' +
                   'greater than the upper bound')
            sys.exit()
        return uniform(lbound, ubound)

    #----------------------------------------------------------

    def subCoords(self, coord1, coord2):
        '''coord1 - coord2'''
        return map(lambda x,y: x-y, coord1, coord2)
    
    def addCoords(self, coord1, coord2):
        '''coord1 + coord2'''
        return map(lambda x,y: x+y, coord1, coord2)

    def mulCoords(self, coef, coord):
        '''coef * coord'''
        return map(lambda x: self.roundInt(1.0*coef*x), coord)
    
    #----------------------------------------------------------

    def getCoordDistance(self, coord1, coord2):
        '''Return the distance between the given two coordinates'''

        d_sqr = 0
        for i in range(0, self.total_dims):
            d_sqr += (coord2[i] - coord1[i])**2
        d = math.sqrt(d_sqr)
        return d

    #----------------------------------------------------------

    def getRandomCoord(self):
        '''Randomly pick a coordinate within the search space'''

        random_coord = []
        for i in range(0, self.total_dims):
            iuplimit = self.dim_uplimits[i]
            ipoint = self.getRandomInt(0, iuplimit-1)
            random_coord.append(ipoint)
        return random_coord
                                                                     
    #----------------------------------------------------------

    def getNeighbors(self, coord, distance):
        '''Return all the neighboring coordinates (within the specified distance)'''
        
        # get all valid distances
        distances = [0] + range(1,distance+1,1) + range(-1,-distance-1,-1)

        # get all neighboring coordinates within the specified distance
        neigh_coords = [[]]
        for i in range(0, self.total_dims):
            iuplimit = self.dim_uplimits[i]
            cur_points = [coord[i]+d for d in distances]
            cur_points = filter(lambda x: 0 <= x < iuplimit, cur_points)
            n_neigh_coords = []
            for ncoord in neigh_coords:
                n_neigh_coords.extend([ncoord[:]+[p] for p in cur_points])
            neigh_coords = n_neigh_coords

        # remove the current coordinate from the neighboring coordinates list
        neigh_coords.remove(coord)
        
        # return all valid neighboring coordinates
        return neigh_coords

    #----------------------------------------------------------

    def searchBestNeighbor(self, coord, distance):
        '''
        Perform a local search by starting from the given coordinate then examining
        the performance costs of the neighboring coordinates (within the specified distance),
        then we perform this local search recursively once the neighbor with the best performance
        cost is found.
        '''

        # get all neighboring coordinates within the specified distance
        neigh_coords = self.getNeighbors(coord, distance)

        # record the best neighboring coordinate and its performance cost so far
        best_coord = coord
        best_perf_cost = self.getPerfCost(coord)

        # examine all neighboring coordinates
        for n in neigh_coords:
            perf_cost = self.getPerfCost(n)
            if perf_cost < best_perf_cost:
                best_coord = n
                best_perf_cost = perf_cost

        # recursively apply this local search, if new best neighboring coordinate is found
        if best_coord != coord:
            return self.searchBestNeighbor(best_coord, distance)
        
        # return the best neighboring coordinate and its performance cost
        return (best_coord, best_perf_cost)
    

