# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPBadRequest

from chsdi.models.bod import Topics


class MapNameValidation(object):

    def hasMap(self, db, mapName):
        availableMaps = [q[0] for q in db.query(Topics.id)]
        # FIXME add this info in DB
        availableMaps.append('all')

        if mapName not in availableMaps:
            raise HTTPBadRequest('The map you provided does not exist')


class BaseValidation(MapNameValidation):

    def __init__(self, request):
        super(BaseValidation, self).__init__()

        self.mapName = request.matchdict.get('map')
        self.hasMap(request.db, self.mapName)
        self.geodataStaging = request.registry.settings['geodata_staging']
        self.cbName = request.params.get('callback')
        self.request = request
        self.lang = request.lang
        self.translate = request.translate


class BaseLayersValidation(BaseValidation):

    def __init__(self, request):
        super(BaseLayersValidation, self).__init__(request)
        self._chargeable = None
        self._srid = 21781

        # Not to be published in doc
        self.chargeable = request.params.get('chargeable')
        self.searchText = request.params.get('searchText')
        self.srid = request.params.get('sr')

    @property
    def chargeable(self):
        return self._chargeable

    @chargeable.setter
    def chargeable(self, value):
        if value is not None:
            if value.lower() == 'true':
                self._chargeable = True
            elif value.lower() == 'false':
                self._chargeable = False

    @property
    def srid(self):
        return self._srid

    @srid.setter
    def srid(self, value):
        if value in ('2056', '2781'):
            self._srid = int(value)
        elif value is not None:
            raise HTTPBadRequest('Unsupported spatial reference %s' % value)


class BaseFeaturesValidation(BaseLayersValidation):

    def __init__(self, request):
        super(BaseFeaturesValidation, self).__init__(request)
        self._geometryFormat = None

        self.geometryFormat = request.params.get('geometryFormat')
        self.varnish_authorized = request.headers.get(
            'X-SearchServer-Authorized', 'false').lower() == 'true'

    @property
    def geometryFormat(self):
        return self._geometryFormat

    @geometryFormat.setter
    def geometryFormat(self, value):
        if value is not None:
            if value == 'geojson':
                self._geometryFormat = value
            else:
                self._geometryFormat = 'esrijson'
