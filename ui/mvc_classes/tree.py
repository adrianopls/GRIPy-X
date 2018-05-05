# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import wx

from basic.uom import uom

from om.Manager import ObjectManager
from ui.uimanager import UIManager
from ui.uimanager import UIControllerBase 
from ui.uimanager import UIViewBase 
from app import log 






class TreeController(UIControllerBase):
    tid = 'tree_controller'
    #_singleton_per_parent = True
    _PSEUDOROOTUID = "__ROOT__"
    _DEFAULT_ROOT_NAME = u"GRIPy Project"
    
    
    def __init__(self): 
        super(TreeController, self).__init__()
        self._mapobjects = {}
        self._maptypes = {}
           
        
    def PostInit(self):
        self._mapobjects[self._PSEUDOROOTUID] = self.view._rootid
        self._maptypes[self._PSEUDOROOTUID] = {} 
        OM = ObjectManager(self)
        OM.subscribe(self.get_treeitem, 'add')
        OM.subscribe(self.remove_treeitem, 'post_remove')

     
    def refresh(self):
        OM = ObjectManager(self)
        for uid, treeid in self._mapobjects.items():
            if uid == self._PSEUDOROOTUID:
                continue
            self.view.SetItemText(treeid, OM.get(uid).name)


    def set_project_name(self, name=wx.EmptyString):
        if name:
            _, name = os.path.split(name)      
        self.view._set_project_name(name)
           

    ###
    

    def get_treeitem(self, objuid):
        # If object's treeitemid already exists, we are done
        #print 'TreeController.get_treeitem:', objuid
					
						   
		 
								
							
        try:
            #print 'self._mapobjects:', self._mapobjects
			   
					   
					
					   
		 
														  
            treeitem = self._mapobjects.get(objuid)
            #print 'treeitem:', treeitem
												
            if treeitem:
             #   print 'treeitem existe, retornando o'
                return treeitem
        except Exception as e:
            #print '\nERROR[0]: TreeController.get_treeitem:', e
            raise
		 
					   


        try:
            #print 'treeitem NAO existe, CRIAR...'
            #print ('1 - Get object_ do OM')
            OM = ObjectManager(self)
            #print ('1.5')
            obj = OM.get(objuid)
            #print ('2')
            try:
                show = obj.SHOW_ON_TREE
            except:
                show = True
            if not show:
                return None
            #print (3)
        except BaseException as e:
            #print '\nERROR[1]: TreeController.get_treeitem:', e
            raise
            
        try:    
            # Else, we will check for object parent treeitemid
            parent_treeitem = self.get_parent_treeitem(objuid)
            # Dealing with object treeitemid creation
            #print (4)
            obj_str = self._get_object_label(objuid)
            treeitem = self.view.AppendItem(parent_treeitem, obj_str)
            #print (5)
            self.view.SetItemData(treeitem, (objuid, None))
            #print (6)
            self._mapobjects[objuid] = treeitem
            self._maptypes[objuid] = {}
            #print (7)
            # Dealing with object attributes
            self._create_object_attributes(objuid)
            #print ('FIM')
            #
            return treeitem
        except BaseException as e:
            #print '\nERROR[2]: TreeController.get_treeitem:', e
            raise

    def _get_object_attributes(self, objuid):
        OM = ObjectManager(self)
        obj = OM.get(objuid)
        ret_list = []
        for attr, attr_label in obj._SHOWN_ATTRIBUTES:
            try:
                value = getattr(obj, attr)
            except:
                value = obj.attributes.get(attr)   
            if isinstance(value, float):
                value = "{0:.2f}".format(value)
            elif value is None:
                value = 'None'
            attr_str = attr_label + ': ' + str(value)  
            ret_list.append(attr_str)
        return ret_list

    
    def _create_object_attributes(self, objuid):
        obj_treeitem = self._mapobjects.get(objuid)
        if not obj_treeitem:
            raise Exception('Creating object attributes for an object not exists.')
        # Create item obj parameters
        try:
            for attr_str in self._get_object_attributes(objuid):
                attrtreeid = self.view.AppendItem(obj_treeitem, attr_str)
                self.view.SetItemData(attrtreeid, (None, None))
        except Exception:
            pass        
 
    
    def _create_tid_data(self, obj, parentuid):
        parent_treeid = self.get_treeitem(parentuid)
        try:
            treeparentid = self.view.AppendItem(parent_treeid, obj._FRIENDLY_NAME)
        except AttributeError:  
            treeparentid = self.view.AppendItem(parent_treeid, obj.tid)
        self.view.SetItemData(treeparentid, (parentuid, obj.tid))
        self._maptypes[parentuid][obj.tid] = treeparentid
        return treeparentid
    
    
    def get_parent_treeitem(self, objuid):
        if objuid !=  self._PSEUDOROOTUID:
            OM = ObjectManager(self)
            obj = OM.get(objuid)
            parentuid = OM._getparentuid(objuid)
        if not parentuid:
            parentuid = self._PSEUDOROOTUID
        treeitem_parent = self._maptypes[parentuid].get(obj.tid)  
        if not treeitem_parent:
            treeitem_parent = self._create_tid_data(obj, parentuid)
        return treeitem_parent   
    

    def _get_object_label(self, objuid):
        OM = ObjectManager(self)
        obj = OM.get(objuid)
        obj_str = obj.name
        # 
        return obj_str

    #"""
    def reload_object(self, objuid):
        treeitem = self._mapobjects.get(objuid)
        if not treeitem:
            raise Exception('Trying to reload an object not exists.')
        self.view.DeleteChildren(treeitem)
        self.view.SetItemText(treeitem, self._get_object_label(objuid))
        self._create_object_attributes(objuid)
    #"""    
    
    """
    def reload_object(self, objuid):
        OM = ObjectManager(self)
        
        treeitem = self._mapobjects.get(objuid)
        if not treeitem:
            raise Exception('Trying to reload an object not exists.')
        #    
        #self.view.DeleteChildren(treeitem)
        
        
        self._reload_object(objuid)
        
        #self.view.SetItemText(treeitem, self._get_object_label(objuid))
        #
        #self.get_treeitem(objuid)
        #self._create_object_attributes(objuid)
        
        #for son in OM.list(parentuidfilter=objuid):
        #    self.reload_object(son.uid)


    def _reload_object(self, objuid):
        OM = ObjectManager(self)
        self.get_treeitem(objuid)    
        for son in OM.list(parentuidfilter=objuid):
            self._reload_object(son.uid)

    
    """    
#    def     
        
        
    def remove_treeitem(self, objuid):
        treeitem = self._mapobjects.get(objuid)
        if not treeitem:
            raise Exception('Removing treeitem for an object not exists.')
        #        
        treeitem_parent = self.view.GetItemParent(treeitem)
        parentuid, tid = self.view.GetItemData(treeitem_parent)
        del self._maptypes[objuid]
        del self._mapobjects[objuid]
        #
        self.view.Delete(treeitem)
        #
        if not self.view.GetChildrenCount(treeitem_parent):
            del self._maptypes[parentuid][objuid[0]]
            self.view.Delete(treeitem_parent)
#        else:
#            raise Exception('')
        return True        







class TreeView(UIViewBase, wx.TreeCtrl):
    tid = 'tree'
    
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)  
        
        wx.TreeCtrl.__init__(self, parent_controller.view, -1, wx.Point(0, 0), wx.Size(200, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        
        self._rootid = self.AddRoot(wx.EmptyString)                  
        self._set_project_name() 
    
        self.SetItemData(self._rootid, (controller._PSEUDOROOTUID, None))
        
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rightclick)     
        
        '''
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)
        items.append(tree.AppendItem(root, "Item 1", 0))
        '''
        parent_controller.view._mgr.AddPane(self, wx.aui.AuiPaneInfo().Name("tree").
                Caption("Object Manager").Left().Layer(1).Position(1).
                PinButton(True).MinimizeButton(True).
                CloseButton(False).MaximizeButton(True)
        )        
        parent_controller.view._mgr.Update()
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag) 



    def _set_project_name(self, name=wx.EmptyString):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if name:          
            self._root_name = controller._DEFAULT_ROOT_NAME + ' [' + name + ']'
        else:
            self._root_name = controller._DEFAULT_ROOT_NAME
        self.SetItemText(self._rootid, self._root_name)   

      
    def _on_begin_drag(self, event):
        item = event.GetItem()
        tree = event.GetEventObject()
        if item == tree.GetRootItem():
            return   
        uid, tree_tid = tree.GetItemData(item)
        if tree_tid is not None:
            # Objects have tree_tid == None
            return
        if uid is None:
            # Object leaf properties
            return
        # Falta tratar Well
        def DoDragDrop():
            data_obj = wx.CustomDataObject('obj_uid')
            data_obj.SetData(str.encode(str(uid)))
            drag_source = wx.DropSource(tree)
            drag_source.SetData(data_obj)    
            drag_source.DoDragDrop()  
            
        # TODO: Verificar se wx.CallAfter pode retornar
        # Motivo: wx.CallAfter não estava funcionando adequadamente em Gtk 
        # no DragAndDrop pois wx.DropSource.DoDragDrop retornava wx.DragNone
        # não permitia entrar no modo Dragging.
        # Essa foi a unica solução encontrada - Adriano - 22/3/2017
        if os.name == 'posix':
            DoDragDrop()
        else:    
            wx.CallAfter(DoDragDrop)



    def on_rightclick(self, event):
        treeid = event.GetItem()
        uid, tree_tid = self.GetItemData(treeid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        OM = ObjectManager(self)
        
        if uid is None:  # Object attributes
            return
        if uid == controller._PSEUDOROOTUID and tree_tid is None:
            return
        #
        self.popup_obj = (uid, tree_tid)
        self.popupmenu = wx.Menu()  
        #
        item = self.popupmenu.Append(wx.NewId(), 'Rename object')
        self.Bind(wx.EVT_MENU, self.OnRenameObject, item)
        self.popupmenu.AppendSeparator()
        #
        if self._is_convertible(uid):
            item = self.popupmenu.Append(wx.NewId(), 'Convert unit')
            self.Bind(wx.EVT_MENU, self.OnUnitConvert, item)
            self.popupmenu.AppendSeparator()
        #
        if tree_tid is not None:
            # Exclude all objects from a class
            menu_option_str = u'Exclude all objects [{}]'.format(tree_tid) 
        else:
            # Exclude a specific object
            obj = OM.get(uid)
            #classid, oid = uid
            menu_option_str = u'Exclude object ['
            menu_option_str = menu_option_str + str(obj.name) + u']'
        #
        item = self.popupmenu.Append(wx.NewId(), menu_option_str)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        #
        pos = event.GetPoint()
        self.PopupMenu(self.popupmenu, pos)


    def _is_convertible(self, uid):
        if uid[0] in ['log', 'data_index']:
            return True
        return False



    def OnPopupItemSelected(self, event):
        uid, tree_tid = self.popup_obj
        OM = ObjectManager(self)
        if tree_tid is None:
            OM.remove(uid)
        else:
            if tree_tid == 'well':
                items = OM.list(tree_tid)
            else:    
                items = OM.list(tree_tid, uid)
            for item in items:
                OM.remove(item.uid)
              


    def OnRenameObject(self, event):  
        uid, tree_tid = self.popup_obj
        OM = ObjectManager(self)       
        obj = OM.get(uid)
        
        UIM = UIManager()
        dlg = UIM.create('dialog_controller', title='Rename object')        
        #
        try:        
            ctn_details = dlg.view.AddCreateContainer('StaticBox', label='Object details', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Name: ' + obj.name)
            #
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Type id: ' + obj.tid)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Object id: ' + str(obj.oid))
            #
            ctn_new_name = dlg.view.AddCreateContainer('StaticBox', label='New name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)  
            dlg.view.AddTextCtrl(ctn_new_name, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_name', initial=obj.name)     
            #    
            dlg.view.SetSize((300, 330))
            answer = dlg.view.ShowModal()
            #
            if answer == wx.ID_OK:
                results = dlg.get_results()  
                new_name = results.get('new_name')
                obj.name = new_name   
                UIM = UIManager()
                controller = UIM.get(self._controller_uid)
                controller.reload_object(obj.uid)                 
        except Exception:
            pass
        finally:
            UIM.remove(dlg.uid)     


                          
    def OnUnitConvert(self, event):     
        uid, tree_tid = self.popup_obj
        OM = ObjectManager(self)       
        obj = OM.get(uid)
        try:
            unit = uom.get_unit(obj.unit)
            dim = uom.get_unit_dimension(unit.dimension)
            qc = uom.get_quantity_class(dim.name)
            UNITS_OPTIONS = OrderedDict()
            for mu in qc.memberUnit:
                UNITS_OPTIONS[mu] = mu 
        except:    
            msg = 'Unit ' + obj.unit + ' cannot be converted.'
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            return 
            #
        UIM = UIManager()
        dlg = UIM.create('dialog_controller', title='Unit conversion')        
        #
        try:
            ctn_details = dlg.view.AddCreateContainer('StaticBox', label='Object details', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Name: ' + obj.name)
            #
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Type id: ' + obj.tid)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Object id: ' + str(obj.oid))
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Current unit: ' + obj.unit)
            #
            ctn_new_unit = dlg.view.AddCreateContainer('StaticBox', label='New unit', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)  
            dlg.view.AddChoice(ctn_new_unit, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_unit', options=UNITS_OPTIONS)     
            #    
            dlg.view.SetSize((300, 330))
            answer = dlg.view.ShowModal()
            #
            if answer == wx.ID_OK:
                results = dlg.get_results()  
                new_unit_name = results.get('new_unit')
                new_data = uom.convert(obj.data, obj.unit, new_unit_name)
                obj._data = new_data
                obj.unit = new_unit_name            
                UIM = UIManager()
                controller = UIM.get(self._controller_uid)
                controller.reload_object(obj.uid)                 
        except Exception:
            pass
        finally:
            UIM.remove(dlg.uid)        
            
        
        
        
        
        
        
        
        