# -*- coding: utf-8 -*-

from sqlalchemy.sql import func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement
from geoalchemy2.types import Geometry


"""
-- custom postgres sql function remove_accents

CREATE OR REPLACE FUNCTION public.remove_accents(string character varying)
  RETURNS character varying AS
$BODY$
    DECLARE
        res varchar;
    BEGIN
        res := replace(string, 'ü', 'ue');
        res := replace(res, 'Ü', 'ue');
        res := replace(res, 'ä', 'ae');
        res := replace(res, 'Ä', 'ae');
        res := replace(res, 'ö', 'oe');
        res := replace(res, 'Ö', 'oe');
        res := replace(res, '(', '_');
        res := replace(res, ')', '_');


        res:= translate(res, 'àáâÀÁÂ', 'aaaaaa');
        res:= translate(res, 'èéêëÈÉÊË', 'eeeeeeee');
        res:= translate(res, 'ìíîïÌÍÎÏ', 'iiiiiiii');
        res:= translate(res, 'òóôÒÓÔ', 'oooooo');
        res:= translate(res, 'ùúûÙÚÛ', 'uuuuuu');
        res:= translate(res, 'ç', 'c');

        RETURN trim(lower(res));
    END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
"""


class remove_accents(FunctionElement):
    name = "remove_accents"


@compiles(remove_accents)
def compile(element, compiler, **kw):
    return "remove_accents(%s)" % compiler.process(element.clauses)


"""
Custom class that extends the base geometry class of geoalchemy2.
This class is used to reproject geometries on the fly so that the reference to
the main model is kept.
"""


class TransformedGeometry(Geometry):

    def __init__(self, geometry_type='GEOMETRY', srid=-1, dimension=2,
                 spatial_index=True, management=False, srid_out=21781):
        super(TransformedGeometry, self).__init__(geometry_type=geometry_type,
              srid=srid, dimension=dimension, spatial_index=spatial_index,
              management=management)
        self._srid_out = int(srid)

    @property
    def srid_out(self):
        return self._srid_out

    @srid_out.setter
    def srid_out(self, value):
        if value in (2056, 21781):
            self._srid_out = value

    def column_expression(self, col):
        if self.srid != self.srid_out:
            col = func.ST_Transform(col, self._srid_out)
        return getattr(func, self.as_binary)(col, type_=self)
