function submit_quickbook_data() {
                                $.ajax({
                                  'url': 'add_quick_b_data',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {
                                    
                                    
                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);

                                  }
                                });
                               
                              }
                        function showSpinner() {
                            var opts = {
                              lines: 15, 
                              length: 3, 
                              width: 4, 
                              radius: 30, 
                              rotate: 0, 
                              color: '#fff', 
                              speed: 2, 
                              trail: 70, 
                              shadow: false, 
                              hwaccel: false, 
                              className: 'spinner', 
                              zIndex: 2e9, 
                              top: 'auto', 
                              left: 'auto' 
                            };
                            $('#loading_anim').each(function() {
                                spinner = new Spinner(opts).spin(this);
                            });
                        }
                        
                        function submit_export_dt_co() {
                                $.ajax({
                                  'url': 'add_export_cust_data',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                        function submit_quickbook_vendor() {
                                $.ajax({
                                  'url': 'add_quick_b_vendor',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                            
                        function export_quickbook_vendor() {
                                $.ajax({
                                  'url': 'export_quick_b_vendor',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                   data = JSON.parse(data);
                                   $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                            
                            function submit_quickbook_accounts() {
                                $.ajax({
                                  'url': 'add_quick_b_account',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function submit_quickbook_items() {
                                $.ajax({
                                  'url': 'add_quick_b_items',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function export_quickbook_items() {
                                $.ajax({
                                  'url': 'export_quick_b_items',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                        
                        
                            function submit_quickbook_invoice() {
                                $.ajax({
                                  'url': 'add_quick_b_invoice',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function export_quickbook_invoice() {
                                $.ajax({
                                  'url': 'export_quick_b_invoice',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = JSON.parse(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function submit_quickbook_purchase() {
                                $.ajax({
                                  'url': 'add_quick_b_purchase',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = $.parseJSON(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function export_quickbook_purchase() {
                                $.ajax({
                                  'url': 'export_quick_b_purchase',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = $.parseJSON(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        
                            function submit_quickbook_sale() {
                                $.ajax({
                                  'url': 'add_quick_b_sale',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = $.parseJSON(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                            function export_quickbook_sale() {
                                $.ajax({
                                  'url': 'export_quick_b_sale',
                                  'type': 'POST',
                                  'data': $('#quickbook_data').serialize(),
                                  'success': function(data) {

                                    data = $.parseJSON(data);
                                    $("#loading").show();
                                    
                                    setTimeout(function() {
                                        setTimeout(function() {showSpinner();},30);
                                        window.location.replace(data['url']);
                                    },0);
                                  }
                                });
                               
                              }
                        