# language: zh-CN
功能: ${name}

% for scenario in scenarios :
  场景: ${scenario.name} 
  % for i, given_step in enumerate(scenario.given_steps) : 
  	% if i == 0 :
      假如 ${given_step} 
    % else :
      而且 ${given_step} 
    % endif
  % endfor
  % for j, when_step in enumerate(scenario.when_steps) :
  	% if j == 0 :
      当   ${when_step} 
    % else : 
      而且 ${when_step} 
    % endif
  % endfor
  % for k, then_step in enumerate(scenario.then_steps) :
  	% if k == 0 :
      那么 ${then_step} 
    % else :
      而且 ${then_step} 
    % endif
  % endfor

% endfor



    